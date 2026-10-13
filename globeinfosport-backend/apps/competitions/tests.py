"""Tests essentiels de l'automatisation sportive."""

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.actualites.models import Pays, Sport
from apps.competitions.models import ClassementLigne, Club, Competition, Match, StatistiqueJoueur
from apps.competitions.serializers import MatchResultatSerializer
from apps.competitions.services.football_data import synchroniser_football_data
from apps.joueurs.models import Joueur, Poste


class ResultatAutomationTests(TestCase):
    """Un score final et ses événements reconstruisent les tableaux dérivés."""

    def setUp(self) -> None:
        self.competition = Competition.objects.create(
            nom="Championnat test",
            type=Competition.Type.CHAMPIONNAT_NATIONAL,
            saison="2026",
        )
        self.domicile = Club.objects.create(nom="Don Bosco")
        self.exterieur = Club.objects.create(nom="Racing CH")
        # Le référentiel est initialisé par une migration : le test reste
        # indépendant de l'ordre des migrations.
        poste, _ = Poste.objects.get_or_create(nom="Attaquant")
        self.buteur = Joueur.objects.create(nom="Pierre", prenom="Jean", poste=poste)
        self.passeur = Joueur.objects.create(nom="Joseph", prenom="Marc", poste=poste)
        self.match = Match.objects.create(
            competition=self.competition,
            club_domicile=self.domicile,
            club_exterieur=self.exterieur,
            date_heure=timezone.now(),
        )

    def test_saisie_resultat_recalcule_classement_et_statistiques(self) -> None:
        serializer = MatchResultatSerializer(
            self.match,
            data={
                "score_domicile": 2,
                "score_exterieur": 1,
                "buteurs": [
                    {
                        "joueur": self.buteur.pk,
                        "passeur": self.passeur.pk,
                        "minute": 37,
                        "type_but": "BUT",
                    }
                ],
            },
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        ligne_domicile = ClassementLigne.objects.get(
            competition=self.competition, club=self.domicile
        )
        ligne_exterieur = ClassementLigne.objects.get(
            competition=self.competition, club=self.exterieur
        )
        self.assertEqual((ligne_domicile.points, ligne_domicile.victoires), (3, 1))
        self.assertEqual((ligne_exterieur.points, ligne_exterieur.defaites), (0, 1))
        self.assertEqual(
            StatistiqueJoueur.objects.get(
                competition=self.competition, joueur=self.buteur
            ).buts,
            1,
        )
        self.assertEqual(
            StatistiqueJoueur.objects.get(
                competition=self.competition, joueur=self.passeur
            ).passes_decisives,
            1,
        )


class MajorLeaguesSeedTests(TestCase):
    def test_seed_creates_the_five_major_leagues_and_their_clubs(self) -> None:
        call_command("seed_editorial")
        premier_league = Competition.objects.get(
            nom="Premier League",
            type=Competition.Type.CHAMPIONNAT_NATIONAL,
            saison="2026-2027",
        )
        self.assertEqual(premier_league.clubs.count(), 20)
        self.assertTrue(premier_league.clubs.filter(nom="Arsenal").exists())

        response = APIClient().get(f"/api/v1/public/competitions/{premier_league.pk}/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data["clubs_detail"]), 20)
        self.assertEqual(response.data["sport_detail"]["nom"], "Football")


class _FootballDataClientStub:
    def teams(self, code):
        assert code == "PL"
        return [
            {"id": 57, "name": "Arsenal"},
            {"id": 58, "name": "Chelsea"},
        ]

    def matches(self, code):
        assert code == "PL"
        return [
            {
                "id": 1001,
                "utcDate": "2026-09-20T15:00:00Z",
                "status": "FINISHED",
                "homeTeam": {"id": 57},
                "awayTeam": {"id": 58},
                "score": {"fullTime": {"home": 2, "away": 1}},
            }
        ]

    def standings(self, code):
        assert code == "PL"
        return [
            {
                "type": "TOTAL",
                "table": [
                    {"team": {"id": 57}, "playedGames": 1, "won": 1, "draw": 0, "lost": 0, "goalsFor": 2, "goalsAgainst": 1, "points": 3},
                    {"team": {"id": 58}, "playedGames": 1, "won": 0, "draw": 0, "lost": 1, "goalsFor": 1, "goalsAgainst": 2, "points": 0},
                ],
            }
        ]


class FootballDataImportTests(TestCase):
    def setUp(self) -> None:
        football = Sport.objects.create(nom="Football")
        angleterre = Pays.objects.create(code="GB", nom="Royaume-Uni", region="Europe")
        self.competition = Competition.objects.create(
            nom="Premier League",
            type=Competition.Type.CHAMPIONNAT_NATIONAL,
            saison="2026-2027",
            sport=football,
            pays=angleterre,
            source_donnees="football-data.org",
            identifiant_source="PL",
        )

    def test_import_updates_clubs_matches_standings_and_is_idempotent(self) -> None:
        resume = synchroniser_football_data(["PL"], client=_FootballDataClientStub())

        self.assertEqual(resume, {"competitions": 1, "equipes": 2, "matchs": 1, "lignes_classement": 2})
        self.assertEqual(self.competition.clubs.count(), 2)
        self.assertIsNotNone(Competition.objects.get(pk=self.competition.pk).derniere_synchronisation)
        self.assertEqual(Match.objects.filter(source_donnees="football-data.org").count(), 1)
        self.assertEqual(
            ClassementLigne.objects.get(competition=self.competition, club__nom="Arsenal").points,
            3,
        )
        classement_response = APIClient().get(
            f"/api/v1/public/classement/{self.competition.pk}/"
        )
        self.assertEqual(classement_response.status_code, 200, classement_response.data)
        classement = classement_response.data.get("results", classement_response.data)
        self.assertEqual(len(classement), 2)
        calendrier_response = APIClient().get(
            "/api/v1/public/matchs/", {"competition": self.competition.pk}
        )
        self.assertEqual(calendrier_response.status_code, 200, calendrier_response.data)
        calendrier = calendrier_response.data.get("results", calendrier_response.data)
        self.assertEqual(len(calendrier), 1)

        synchroniser_football_data(["PL"], client=_FootballDataClientStub())
        self.assertEqual(Match.objects.filter(source_donnees="football-data.org").count(), 1)
        self.assertEqual(self.competition.clubs.count(), 2)
