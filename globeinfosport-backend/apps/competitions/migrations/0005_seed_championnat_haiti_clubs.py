"""Enrichit le référentiel des clubs du Championnat haïtien.

Les données proviennent de la liste des clubs de l'édition 2020-2021 et du
tableau du palmarès publiés dans l'article Wikipédia consacré au Championnat
d'Haïti de football, consulté le 8 septembre 2026. Elles restent éditables
dans le back-office : cette migration ne remplace jamais un texte déjà saisi
par la rédaction.
"""

from django.db import migrations
from django.utils.text import slugify


CHAMPIONNAT = "Championnat haïtien de football"

# ``ville`` et ``stade`` conservent les précisions utiles à la vitrine, dont
# le département et la capacité lorsque celles-ci sont documentées.
CLUBS = (
    {
        "nom": "América des Cayes",
        "ville": "Les Cayes, Sud",
        "stade": "Parc Larco (2 000 places)",
        "titres": ("2014 — Ouverture",),
    },
    {
        "nom": "Arcahaie FC",
        "ville": "Arcahaie, Ouest",
        "stade": "Parc Saint-Yves (1 000 places)",
        "titres": ("2019 — Ouverture",),
    },
    {
        "nom": "AS Capoise",
        "ville": "Cap-Haïtien, Nord",
        "stade": "Parc Saint-Victor (9 500 places)",
        "titres": ("1997", "2017 — Clôture", "2018 — Ouverture"),
    },
    {
        "nom": "AS Mirebalais",
        "ville": "Mirebalais, Centre",
        "stade": "Parc Nelson-Petit-Frère (2 000 places)",
        "titres": ("2004-2005 — Ouverture", "2013"),
    },
    {
        "nom": "Baltimore SC",
        "ville": "Saint-Marc, Artibonite",
        "stade": "Parc Levelt (5 000 places)",
        "titres": (
            "2004-2005 — Clôture",
            "2005-2006 — Ouverture",
            "2007 — Ouverture",
            "2011 — Ouverture",
        ),
    },
    {
        # Le référentiel initial du projet emploie cet ordre de nom.
        "nom": "Cavaly AS",
        "ville": "Léogâne, Ouest",
        "stade": "Parc Julia-Vilbon (10 500 places)",
        "titres": ("2007 — Clôture",),
    },
    {
        "nom": "Cosmopolites SC",
        "ville": "Delmas, Ouest",
        "stade": "",
        "titres": (),
    },
    {
        "nom": "Don Bosco FC",
        "ville": "Pétion-Ville, Ouest",
        "stade": "Stade Sylvio-Cator (15 000 places)",
        "titres": (
            "1971",
            "2003 — Ouverture",
            "2014 — Clôture",
            "2015 — Ouverture",
            "2018 — Clôture",
        ),
    },
    {
        "nom": "FICA",
        "ville": "Cap-Haïtien, Nord",
        "stade": "Parc Saint-Victor (9 500 places)",
        "titres": (
            "1988-1989",
            "1990",
            "1993-1994",
            "1998",
            "2001",
            "2015 — Clôture",
            "2016 — Clôture",
        ),
    },
    {
        "nom": "Juventus des Cayes",
        "ville": "Les Cayes, Sud",
        "stade": "",
        "titres": ("2025",),
    },
    {
        "nom": "Ouanaminthe FC",
        "ville": "Ouanaminthe, Nord-Est",
        "stade": "Parc Notre-Dame de Vapor (1 000 places)",
        "titres": (),
    },
    {
        "nom": "Racing Club Haïtien",
        "ville": "Port-au-Prince, Ouest",
        "stade": "Stade Sylvio-Cator (15 000 places)",
        "titres": (
            "1937-1938",
            "1941",
            "1946",
            "1947",
            "1953-1954",
            "1958",
            "1962",
            "1969",
            "2000",
            "2002 — Clôture",
            "2009 — Clôture",
        ),
    },
    {
        "nom": "Racing Gonaïves",
        "ville": "Les Gonaïves, Artibonite",
        "stade": "Parc Stenio-Vincent (3 000 places)",
        "titres": ("1996", "2008 — Clôture", "2016 — Ouverture"),
    },
    {
        "nom": "Real Hope FA",
        "ville": "Cap-Haïtien, Nord",
        "stade": "Parc Saint-Victor (9 500 places)",
        "titres": ("2017 — Ouverture", "2024"),
    },
    {
        "nom": "Tempête FC",
        "ville": "Saint-Marc, Artibonite",
        "stade": "Parc Levelt (5 000 places)",
        "titres": (
            "1992-1993",
            "2008 — Ouverture",
            "2009 — Ouverture",
            "2010-2011 — Ouverture",
            "2011 — Clôture",
        ),
    },
    {
        "nom": "Triomphe AC",
        "ville": "Liancourt, Artibonite",
        "stade": "Parc Mercinus-Deslouches (1 000 places)",
        "titres": (),
    },
    {
        "nom": "USR",
        "ville": "Petite-Rivière-de-l'Artibonite, Artibonite",
        "stade": "",
        "titres": (),
    },
    {
        "nom": "Violette AC",
        "ville": "Port-au-Prince, Ouest",
        "stade": "Stade Sylvio-Cator (15 000 places)",
        "titres": (
            "1939",
            "1957",
            "1968",
            "1983",
            "1994-1995",
            "1999",
            "2020-2021 — Ouverture",
        ),
    },
)


def _unique_slug(Club, club, nom):
    """Retourne un slug stable sans supposer que tous les noms sont uniques."""

    base = slugify(nom) or f"club-{club.pk}"
    candidate, suffix = base, 2
    while Club.objects.exclude(pk=club.pk).filter(slug=candidate).exists():
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def _profile_text(nom, ville, titres):
    """Produit une introduction originale, limitée aux faits référencés."""

    description = (
        f"{nom} est un club de football basé à {ville}. Il fait partie des "
        "clubs répertoriés pour l'édition 2020-2021 du Championnat haïtien "
        "de football."
    )
    if titres:
        history = (
            f"Le parcours national de {nom} compte {len(titres)} "
            f"titre{'s' if len(titres) > 1 else ''} de champion recensé"
            f"{'s' if len(titres) > 1 else ''}, de {titres[0]} à "
            f"{titres[-1]}. Cette fiche peut être enrichie par la rédaction "
            "avec les archives et témoignages validés du club."
        )
        palmares = (
            f"Championnat d'Haïti — {len(titres)} titre"
            f"{'s' if len(titres) > 1 else ''}\n" + ", ".join(titres)
        )
    else:
        history = (
            f"{nom} figure dans la liste des équipes de l'édition 2020-2021. "
            "La source consultée documente sa localisation mais ne fournit "
            "pas de récit institutionnel détaillé ; la rédaction pourra "
            "compléter les jalons historiques avec des sources du club ou de la FHF."
        )
        palmares = "Aucun titre de champion n'est répertorié pour ce club dans le bilan de la source."
    return description, history, palmares


def seed_championnat_haiti(apps, schema_editor):
    Club = apps.get_model("competitions", "Club")
    ParcoursClub = apps.get_model("competitions", "ParcoursClub")

    for profile in CLUBS:
        nom = profile["nom"]
        club, created = Club.objects.get_or_create(nom=nom)
        description, histoire, palmares = _profile_text(
            nom, profile["ville"], profile["titres"]
        )

        # Préserver tout contenu éditorial existant. Les clubs créés par la
        # migration, comme les champs encore vides, reçoivent le référentiel.
        changed_fields = []
        values = {
            "ville": profile["ville"],
            "stade": profile["stade"],
            "description": description,
            "histoire": histoire,
            "palmares": palmares,
        }
        for field, value in values.items():
            if value and not getattr(club, field):
                setattr(club, field, value)
                changed_fields.append(field)
        if not club.slug:
            club.slug = _unique_slug(Club, club, nom)
            changed_fields.append("slug")
        if changed_fields:
            club.save(update_fields=changed_fields)

        for ordre, saison in enumerate(profile["titres"], start=1):
            ParcoursClub.objects.get_or_create(
                club=club,
                saison=saison,
                competition=CHAMPIONNAT,
                defaults={
                    "position_finale": "Champion",
                    "bilan": "Titre de champion national",
                    "recit": f"{nom} est crédité du titre de champion pour cette édition.",
                    "ordre": ordre,
                },
            )


def unseed_championnat_haiti(apps, schema_editor):
    """Ne jamais supprimer les données éditoriales lors d'un rollback."""


class Migration(migrations.Migration):
    dependencies = [("competitions", "0004_club_profiles")]

    operations = [migrations.RunPython(seed_championnat_haiti, unseed_championnat_haiti)]
