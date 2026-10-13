"""Import idempotent des compétitions couvertes par football-data.org."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.competitions.models import ClassementLigne, Club, Competition, Match


SOURCE = "football-data.org"
SUPPORTED_CODES = ("PL", "PD", "SA", "BL1", "FL1")


class FootballDataConfigurationError(RuntimeError):
    """La clé de l'API sportive n'est pas encore configurée."""


class FootballDataRequestError(RuntimeError):
    """Le fournisseur de données n'a pas pu répondre correctement."""


@dataclass
class SynchronisationResume:
    competitions: int = 0
    equipes: int = 0
    matchs: int = 0
    lignes_classement: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "competitions": self.competitions,
            "equipes": self.equipes,
            "matchs": self.matchs,
            "lignes_classement": self.lignes_classement,
        }


class FootballDataClient:
    """Client HTTP minimal, isolé pour rendre l'import testable."""

    def __init__(self, token: str | None = None, session: requests.Session | None = None):
        self.token = token or settings.FOOTBALL_DATA_API_TOKEN
        self.session = session or requests.Session()
        self.base_url = settings.FOOTBALL_DATA_API_URL
        if not self.token:
            raise FootballDataConfigurationError(
                "FOOTBALL_DATA_API_TOKEN doit être défini avant toute synchronisation."
            )

    def _get(self, path: str) -> dict[str, Any]:
        try:
            response = self.session.get(
                f"{self.base_url}/{path.lstrip('/')}",
                headers={"X-Auth-Token": self.token},
                timeout=20,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise FootballDataRequestError("La source de données sportives est indisponible.") from exc
        payload = response.json()
        if not isinstance(payload, dict):
            raise FootballDataRequestError("Réponse de données sportives invalide.")
        return payload

    def teams(self, code: str) -> list[dict[str, Any]]:
        return list(self._get(f"competitions/{code}/teams").get("teams", []))

    def matches(self, code: str) -> list[dict[str, Any]]:
        return list(self._get(f"competitions/{code}/matches").get("matches", []))

    def standings(self, code: str) -> list[dict[str, Any]]:
        return list(self._get(f"competitions/{code}/standings").get("standings", []))


def _identity(value: str) -> str:
    """Rapproche les noms d'équipes sans remplacer le nom éditorial affiché."""

    simplified = re.sub(r"\b(?:afc|ac|fc|cf|sc|ss|as)\b", "", value.casefold())
    return re.sub(r"[^a-z0-9]", "", simplified)


def _date_heure(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed


def _statut(value: str | None) -> str:
    if value in {"FINISHED", "AWARDED"}:
        return Match.Statut.TERMINE
    if value in {"IN_PLAY", "PAUSED"}:
        return Match.Statut.EN_COURS
    if value in {"POSTPONED", "SUSPENDED", "CANCELLED"}:
        return Match.Statut.REPORTE
    return Match.Statut.A_VENIR


def _score(score: dict[str, Any], side: str) -> int | None:
    for phase in ("fullTime", "regularTime", "halfTime"):
        candidate = score.get(phase) or {}
        if candidate.get(side) is not None:
            return candidate[side]
    return None


def _competition(code: str) -> Competition:
    try:
        return Competition.objects.select_related("sport", "pays").get(
            source_donnees=SOURCE,
            identifiant_source=code,
        )
    except Competition.DoesNotExist as exc:
        raise FootballDataConfigurationError(
            f"Aucune compétition Globe Info Sport n'est reliée au code {code}."
        ) from exc


def _clubs_for_competition(
    competition: Competition, teams: Iterable[dict[str, Any]], resume: SynchronisationResume
) -> dict[str, Club]:
    clubs_by_source = {
        club.identifiant_source: club
        for club in Club.objects.filter(source_donnees=SOURCE).exclude(identifiant_source="")
    }
    clubs_by_identity = {_identity(club.nom): club for club in competition.clubs.all()}
    resolved: dict[str, Club] = {}

    for team in teams:
        identifier = str(team.get("id", ""))
        name = str(team.get("name") or team.get("shortName") or "").strip()
        if not identifier or not name:
            continue
        club = clubs_by_source.get(identifier) or clubs_by_identity.get(_identity(name))
        if club is None:
            club = Club.objects.filter(nom=name).first()
        if club is None:
            club = Club.objects.create(
                nom=name,
                sport=competition.sport,
                pays=competition.pays,
                source_donnees=SOURCE,
                identifiant_source=identifier,
            )
            resume.equipes += 1
        else:
            updates: dict[str, Any] = {}
            if club.sport_id is None:
                updates["sport"] = competition.sport
            if club.pays_id is None:
                updates["pays"] = competition.pays
            if not club.source_donnees:
                updates["source_donnees"] = SOURCE
            if not club.identifiant_source:
                updates["identifiant_source"] = identifier
            if updates:
                for field, field_value in updates.items():
                    setattr(club, field, field_value)
                club.save(update_fields=[*updates, "updated_at"])
        competition.clubs.add(club)
        resolved[identifier] = club
    return resolved


def _synchroniser_matchs(
    competition: Competition,
    fixtures: Iterable[dict[str, Any]],
    clubs: dict[str, Club],
    resume: SynchronisationResume,
) -> None:
    for fixture in fixtures:
        identifier = str(fixture.get("id", ""))
        home = clubs.get(str((fixture.get("homeTeam") or {}).get("id", "")))
        away = clubs.get(str((fixture.get("awayTeam") or {}).get("id", "")))
        kickoff = fixture.get("utcDate")
        if not identifier or not home or not away or not kickoff:
            continue
        score = fixture.get("score") or {}
        defaults = {
            "competition": competition,
            "club_domicile": home,
            "club_exterieur": away,
            "adversaire_texte": "",
            "date_heure": _date_heure(kickoff),
            "score_domicile": _score(score, "home"),
            "score_exterieur": _score(score, "away"),
            "statut": _statut(fixture.get("status")),
        }
        Match.objects.update_or_create(
            source_donnees=SOURCE,
            identifiant_source=identifier,
            defaults=defaults,
        )
        resume.matchs += 1


def _synchroniser_classement(
    competition: Competition, standings: Iterable[dict[str, Any]], clubs: dict[str, Club], resume: SynchronisationResume
) -> None:
    total = next((standing for standing in standings if standing.get("type") == "TOTAL"), None)
    if not total:
        return
    table = total.get("table") or []
    if not table:
        return
    imported_ids: set[int] = set()
    with transaction.atomic():
        for row in table:
            club = clubs.get(str((row.get("team") or {}).get("id", "")))
            if not club:
                continue
            imported_ids.add(club.pk)
            ClassementLigne.objects.update_or_create(
                competition=competition,
                club=club,
                defaults={
                    "matchs_joues": row.get("playedGames", 0),
                    "victoires": row.get("won", 0),
                    "nuls": row.get("draw", 0),
                    "defaites": row.get("lost", 0),
                    "buts_pour": row.get("goalsFor", 0),
                    "buts_contre": row.get("goalsAgainst", 0),
                    "points": row.get("points", 0),
                },
            )
            resume.lignes_classement += 1
        if imported_ids:
            ClassementLigne.objects.filter(competition=competition).exclude(club_id__in=imported_ids).delete()


def synchroniser_football_data(
    codes: Iterable[str] | None = None, client: FootballDataClient | None = None
) -> dict[str, int]:
    """Met à jour équipes, calendrier, résultats et classement des ligues choisies."""

    client = client or FootballDataClient()
    resume = SynchronisationResume()
    wanted_codes = tuple(codes or SUPPORTED_CODES)
    invalid_codes = set(wanted_codes) - set(SUPPORTED_CODES)
    if invalid_codes:
        raise ValueError(f"Compétitions non prises en charge : {', '.join(sorted(invalid_codes))}.")

    for code in wanted_codes:
        competition = _competition(code)
        clubs = _clubs_for_competition(competition, client.teams(code), resume)
        _synchroniser_matchs(competition, client.matches(code), clubs, resume)
        _synchroniser_classement(competition, client.standings(code), clubs, resume)
        competition.derniere_synchronisation = timezone.now()
        competition.save(update_fields=["derniere_synchronisation"])
        resume.competitions += 1
    return resume.as_dict()
