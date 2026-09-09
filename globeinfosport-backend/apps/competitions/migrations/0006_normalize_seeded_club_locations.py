"""Complète les départements des sept clubs issus du référentiel initial."""

from django.db import migrations


LOCATIONS = {
    "AS Capoise": ("Cap-Haïtien", "Cap-Haïtien, Nord"),
    "Baltimore SC": ("Saint-Marc", "Saint-Marc, Artibonite"),
    "Cavaly AS": ("Léogâne", "Léogâne, Ouest"),
    "Don Bosco FC": ("Pétion-Ville", "Pétion-Ville, Ouest"),
    "Racing Club Haïtien": ("Port-au-Prince", "Port-au-Prince, Ouest"),
    "Tempête FC": ("Saint-Marc", "Saint-Marc, Artibonite"),
    "Violette AC": ("Port-au-Prince", "Port-au-Prince, Ouest"),
}


def normalize_locations(apps, schema_editor):
    Club = apps.get_model("competitions", "Club")
    for nom, (old_value, new_value) in LOCATIONS.items():
        Club.objects.filter(nom=nom, ville=old_value).update(ville=new_value)


class Migration(migrations.Migration):
    dependencies = [("competitions", "0005_seed_championnat_haiti_clubs")]

    operations = [migrations.RunPython(normalize_locations, migrations.RunPython.noop)]
