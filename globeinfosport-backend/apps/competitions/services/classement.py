"""Calcul déterministe du classement depuis les résultats terminés."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from django.db import transaction

from apps.competitions.models import ClassementLigne, Competition, Match

if TYPE_CHECKING:
    from apps.competitions.models import Club


def recalculer_classement(match: Match) -> None:
    """Reconstruit le classement de la compétition du match fourni.

    Le calcul porte sur l'ensemble des résultats finalisés plutôt que sur une
    incrémentation. Une correction de score reste donc toujours cohérente.
    """

    recalculer_classement_competition(match.competition)


def recalculer_classement_competition(competition: Competition) -> None:
    """Reconstruit toutes les lignes de classement d'une compétition."""

    # Les matchs contre un adversaire libre (sans Club) ne participent pas au
    # classement local : il n'existe pas de seconde équipe à classer.
    matchs = (
        Match.objects.filter(
            competition=competition,
            statut=Match.Statut.TERMINE,
            score_domicile__isnull=False,
            score_exterieur__isnull=False,
            club_exterieur__isnull=False,
        )
        .select_related("club_domicile", "club_exterieur")
        .order_by("pk")
    )
    statistiques: dict[int, dict[str, int]] = defaultdict(
        lambda: {
            "matchs_joues": 0,
            "victoires": 0,
            "nuls": 0,
            "defaites": 0,
            "buts_pour": 0,
            "buts_contre": 0,
            "points": 0,
        }
    )
    clubs: dict[int, Club] = {}

    for match in matchs:
        domicile, exterieur = match.club_domicile, match.club_exterieur
        if exterieur is None:  # garde défensive, filtré au niveau SQL
            continue
        clubs[domicile.pk] = domicile
        clubs[exterieur.pk] = exterieur

        domicile_stats = statistiques[domicile.pk]
        exterieur_stats = statistiques[exterieur.pk]
        domicile_stats["matchs_joues"] += 1
        exterieur_stats["matchs_joues"] += 1
        domicile_stats["buts_pour"] += match.score_domicile
        domicile_stats["buts_contre"] += match.score_exterieur
        exterieur_stats["buts_pour"] += match.score_exterieur
        exterieur_stats["buts_contre"] += match.score_domicile

        if match.score_domicile == match.score_exterieur:
            domicile_stats["nuls"] += 1
            exterieur_stats["nuls"] += 1
            domicile_stats["points"] += 1
            exterieur_stats["points"] += 1
        elif match.score_domicile > match.score_exterieur:
            domicile_stats["victoires"] += 1
            domicile_stats["points"] += 3
            exterieur_stats["defaites"] += 1
        else:
            exterieur_stats["victoires"] += 1
            exterieur_stats["points"] += 3
            domicile_stats["defaites"] += 1

    with transaction.atomic():
        existing_ids = set(
            ClassementLigne.objects.filter(competition=competition).values_list(
                "club_id", flat=True
            )
        )
        active_ids = set(clubs)
        stale_ids = existing_ids - active_ids
        if stale_ids:
            ClassementLigne.objects.filter(
                competition=competition, club_id__in=stale_ids
            ).delete()

        for club_id, club in clubs.items():
            ClassementLigne.objects.update_or_create(
                competition=competition,
                club=club,
                defaults=statistiques[club_id],
            )
