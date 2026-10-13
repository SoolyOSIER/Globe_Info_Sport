"""Initialisation idempotente des référentiels Globe Info Sport."""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.actualites.models import Categorie, Pays, Sport
from apps.competitions.models import Club, Competition


MAJOR_FIRST_DIVISIONS = (
    {
        "nom": "Premier League",
        "code_source": "PL",
        "pays": "GB",
        "description": "Première division masculine d’Angleterre.",
        "clubs": (
            "Arsenal", "Aston Villa", "AFC Bournemouth", "Brentford", "Brighton & Hove Albion",
            "Chelsea", "Coventry City", "Crystal Palace", "Everton", "Fulham", "Hull City",
            "Ipswich Town", "Leeds United", "Liverpool", "Manchester City", "Manchester United",
            "Newcastle United", "Nottingham Forest", "Sunderland", "Tottenham Hotspur",
        ),
    },
    {
        "nom": "LaLiga EA Sports",
        "code_source": "PD",
        "pays": "ES",
        "description": "Première division masculine d’Espagne.",
        "clubs": (
            "Athletic Club", "Atlético de Madrid", "CA Osasuna", "Celta", "Deportivo Alavés",
            "Elche CF", "FC Barcelona", "Getafe CF", "Levante UD", "Málaga CF", "Real Racing Club",
            "Rayo Vallecano", "RC Deportivo", "RCD Espanyol", "Real Betis", "Real Madrid",
            "Real Sociedad", "Sevilla FC", "Valencia CF", "Villarreal CF",
        ),
    },
    {
        "nom": "Serie A",
        "code_source": "SA",
        "pays": "IT",
        "description": "Première division masculine d’Italie.",
        "clubs": (
            "Atalanta", "Bologna", "Cagliari", "Como", "Fiorentina", "Frosinone", "Genoa", "Inter",
            "Juventus", "Lazio", "Lecce", "Milan", "Monza", "Napoli", "Parma", "Roma", "Sassuolo",
            "Torino", "Udinese", "Venezia",
        ),
    },
    {
        "nom": "Bundesliga",
        "code_source": "BL1",
        "pays": "DE",
        "description": "Première division masculine d’Allemagne.",
        "clubs": (
            "FC Augsburg", "1. FC Union Berlin", "SV Werder Bremen", "Borussia Dortmund", "SV Elversberg",
            "Eintracht Frankfurt", "SC Freiburg", "Hamburger SV", "TSG Hoffenheim", "1. FC Köln",
            "RB Leipzig", "Bayer 04 Leverkusen", "1. FSV Mainz 05", "Borussia Mönchengladbach",
            "FC Bayern München", "SC Paderborn 07", "FC Schalke 04", "VfB Stuttgart",
        ),
    },
    {
        "nom": "Ligue 1 McDonald’s",
        "code_source": "FL1",
        "pays": "FR",
        "description": "Première division masculine de France.",
        "clubs": (
            "Angers SCO", "AJ Auxerre", "Stade Brestois 29", "Havre AC", "Le Mans FC", "RC Lens",
            "FC Lorient", "LOSC Lille", "Olympique Lyonnais", "Olympique de Marseille", "AS Monaco",
            "OGC Nice", "Paris FC", "Paris Saint-Germain", "Stade Rennais FC", "RC Strasbourg Alsace",
            "Toulouse FC", "ESTAC Troyes",
        ),
    },
)


class Command(BaseCommand):
    help = "Initialise les référentiels, sans créer d’actualités ni modifier les contenus existants."

    @transaction.atomic
    def handle(self, *args, **options):
        for nom in [
            "Football", "Basketball", "Volleyball", "Tennis", "Athlétisme", "Natation", "Cyclisme",
            "Boxe", "MMA", "Judo", "Karaté", "Rugby", "Cricket", "Baseball", "Hockey", "Formule 1",
            "Moto", "Golf", "Handball", "Esport", "Jeux olympiques",
        ]:
            Sport.objects.get_or_create(nom=nom)

        for code, nom, region in [
            ("HT", "Haïti", "Caraïbes"), ("FR", "France", "Europe"), ("GB", "Royaume-Uni", "Europe"),
            ("ES", "Espagne", "Europe"), ("IT", "Italie", "Europe"), ("DE", "Allemagne", "Europe"),
            ("US", "États-Unis", "Amérique du Nord"), ("CA", "Canada", "Amérique du Nord"),
            ("MX", "Mexique", "Amérique du Nord"), ("BR", "Brésil", "Amérique du Sud"),
            ("AR", "Argentine", "Amérique du Sud"), ("JP", "Japon", "Asie"),
            ("AU", "Australie", "Océanie"), ("NZ", "Nouvelle-Zélande", "Océanie"),
            ("MA", "Maroc", "Afrique"), ("SN", "Sénégal", "Afrique"), ("CI", "Côte d’Ivoire", "Afrique"),
            ("JM", "Jamaïque", "Caraïbes"), ("DO", "République dominicaine", "Caraïbes"),
            ("CR", "Costa Rica", "Amérique centrale"), ("PA", "Panama", "Amérique centrale"),
        ]:
            Pays.objects.get_or_create(code=code, defaults={"nom": nom, "region": region})

        for nom in [
            "Actualité", "Breaking News", "Match", "Résultat", "Transfert", "Mercato", "Portrait",
            "Interview", "Analyse", "Reportage", "Opinion", "Sélection nationale", "Club", "Joueur",
            "Entraîneur", "Fédération", "Technologie sportive", "Santé sportive", "Autres",
        ]:
            Categorie.objects.get_or_create(nom=nom)

        football = Sport.objects.get(nom="Football")
        clubs_seeded = 0
        for division in MAJOR_FIRST_DIVISIONS:
            pays = Pays.objects.get(code=division["pays"])
            competition, _ = Competition.objects.get_or_create(
                nom=division["nom"],
                type=Competition.Type.CHAMPIONNAT_NATIONAL,
                saison="2026-2027",
                defaults={
                    "sport": football,
                    "pays": pays,
                    "description": division["description"],
                    "actif": True,
                    "source_donnees": "football-data.org",
                    "identifiant_source": division["code_source"],
                },
            )
            updates = {}
            if competition.sport_id is None:
                updates["sport"] = football
            if competition.pays_id is None:
                updates["pays"] = pays
            if not competition.description:
                updates["description"] = division["description"]
            if not competition.source_donnees:
                updates["source_donnees"] = "football-data.org"
            if not competition.identifiant_source:
                updates["identifiant_source"] = division["code_source"]
            if updates:
                for field, value in updates.items():
                    setattr(competition, field, value)
                competition.save(update_fields=[*updates, "actif"])

            for nom_club in division["clubs"]:
                club, created = Club.objects.get_or_create(
                    nom=nom_club,
                    defaults={"sport": football, "pays": pays},
                )
                if created:
                    clubs_seeded += 1
                updates = {}
                if club.sport_id is None:
                    updates["sport"] = football
                if club.pays_id is None:
                    updates["pays"] = pays
                if updates:
                    for field, value in updates.items():
                        setattr(club, field, value)
                    club.save(update_fields=[*updates, "updated_at"])
                competition.clubs.add(club)

        self.stdout.write(
            self.style.SUCCESS(
                f"Référentiels internationaux initialisés ; {clubs_seeded} clubs ajoutés aux cinq grands championnats."
            )
        )
