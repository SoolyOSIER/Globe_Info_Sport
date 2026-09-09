"""Initialise les catégories éditoriales proposées dans le plan produit."""

from django.db import migrations


CATEGORIES_STANDARDS = (
    ("Sélection nationale", "selection-nationale"),
    ("Championnat", "championnat"),
    ("International", "international"),
    ("Portrait", "portrait"),
)


def seed_categories(apps, schema_editor):
    Categorie = apps.get_model("actualites", "Categorie")
    for nom, slug in CATEGORIES_STANDARDS:
        Categorie.objects.get_or_create(nom=nom, defaults={"slug": slug})


def unseed_categories(apps, schema_editor):
    Categorie = apps.get_model("actualites", "Categorie")
    Categorie.objects.filter(
        slug__in=[slug for _, slug in CATEGORIES_STANDARDS],
        articles__isnull=True,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("actualites", "0002_initial")]

    operations = [migrations.RunPython(seed_categories, unseed_categories)]
