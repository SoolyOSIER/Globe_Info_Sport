"""Initialise les postes de football utilisés par les fiches joueurs."""

from django.db import migrations


POSTES_STANDARDS = ("Gardien", "Défenseur", "Milieu", "Attaquant")


def seed_postes(apps, schema_editor):
    Poste = apps.get_model("joueurs", "Poste")
    for nom in POSTES_STANDARDS:
        Poste.objects.get_or_create(nom=nom)


def unseed_postes(apps, schema_editor):
    Poste = apps.get_model("joueurs", "Poste")
    Poste.objects.filter(nom__in=POSTES_STANDARDS, joueurs__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [("joueurs", "0001_initial")]

    operations = [migrations.RunPython(seed_postes, unseed_postes)]
