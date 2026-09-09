"""Initialise les référentiels sportifs nécessaires au calendrier."""

from django.db import migrations


COMPETITIONS = (
    ("Championnat National", "CHAMPIONNAT_NATIONAL", "2026-2027"),
    ("Éliminatoires Coupe du Monde", "ELIMINATOIRES_CDM", "2026"),
    ("Ligue des Nations CONCACAF", "LIGUE_NATIONS", "2026-2027"),
)

CLUBS = (
    ("AS Capoise", "Cap-Haïtien"),
    ("Baltimore SC", "Saint-Marc"),
    ("Cavaly AS", "Léogâne"),
    ("Don Bosco FC", "Pétion-Ville"),
    ("Racing Club Haïtien", "Port-au-Prince"),
    ("Tempête FC", "Saint-Marc"),
    ("Violette AC", "Port-au-Prince"),
)


def seed_references(apps, schema_editor):
    Competition = apps.get_model("competitions", "Competition")
    Club = apps.get_model("competitions", "Club")
    for nom, type_competition, saison in COMPETITIONS:
        Competition.objects.get_or_create(
            nom=nom,
            type=type_competition,
            saison=saison,
            defaults={"actif": True},
        )
    for nom, ville in CLUBS:
        Club.objects.get_or_create(nom=nom, defaults={"ville": ville})


def unseed_references(apps, schema_editor):
    Competition = apps.get_model("competitions", "Competition")
    Club = apps.get_model("competitions", "Club")
    Competition.objects.filter(
        nom__in=[nom for nom, _, _ in COMPETITIONS],
        matchs__isnull=True,
    ).delete()
    Club.objects.filter(
        nom__in=[nom for nom, _ in CLUBS],
        matchs_domicile__isnull=True,
        matchs_exterieur__isnull=True,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("competitions", "0002_buteurmatch_passeur_participationmatch_and_more")]

    operations = [migrations.RunPython(seed_references, unseed_references)]
