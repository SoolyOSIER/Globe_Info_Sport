"""Tests essentiels de l'automatisation sportive."""

from django.test import TestCase
from django.utils import timezone

from apps.competitions.models import ClassementLigne, Club, Competition, Match, StatistiqueJoueur
from apps.competitions.serializers import MatchResultatSerializer
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
        poste = Poste.objects.create(nom="Attaquant")
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
