"""Isolated, loopback-only API for browser tests. Never uses dev.sqlite3."""
import os
from pathlib import Path
import sys
import uuid

backend = Path(__file__).resolve().parents[1] / "globeinfosport-backend"
sys.path.insert(0, str(backend))
os.environ["DATABASE_URL"] = "sqlite:///" + (backend / f"e2e-{uuid.uuid4().hex}.sqlite3").as_posix()
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
os.environ["CELERY_TASK_ALWAYS_EAGER"] = "True"
os.environ["ALLOWED_HOSTS"] = "localhost,127.0.0.1"
os.environ["DEBUG"] = "True"

import django
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
settings.CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
call_command("migrate", interactive=False, verbosity=0)

from apps.comptes.models import RoleRedaction, Utilisateur
from apps.actualites.models import Article, Categorie, Sport, Pays
from apps.competitions.models import Club, Competition, Match
from apps.joueurs.models import Joueur

# Nonstandard ids detect accidental frontend assumptions about role ids.
for pk, role, login in [(31, "ADMINISTRATEUR", "e2e-admin"), (32, "EDITEUR_EN_CHEF", "e2e-editor"), (33, "REDACTEUR", "e2e-writer")]:
    value, _ = RoleRedaction.objects.get_or_create(nomRole=role, defaults={"pk": pk})
    Utilisateur.objects.create_user(login, "BrowserTest!2026", nom=login, role_redaction=value)
sport = Sport.objects.create(nom="Sport de test")
country = Pays.objects.create(nom="Pays de test", code="TT", region="Caraïbes")
category = Categorie.objects.create(nom="Tests navigateur")
author = Utilisateur.objects.get(identifiant="e2e-writer")
Article.objects.create(titre="Brouillon de test", chapo="Chapeau", contenu="<p>Contenu initial</p>", categorie=category, auteur=author)
home = Club.objects.create(nom="Equipe A de test", sport=sport, pays=country)
away = Club.objects.create(nom="Equipe B de test", sport=sport, pays=country)
competition = Competition.objects.create(nom="Competition de test", type="AUTRE", saison="2026", sport=sport, pays=country)
Match.objects.create(competition=competition, club_domicile=home, club_exterieur=away, date_heure=timezone.now())
Joueur.objects.create(nom="Athlete de test", sport=sport, pays=country)
# References beyond the API's first page must remain selectable.
for index in range(105):
    Club.objects.create(nom=f"Reference club {index:03}")
call_command("runserver", "127.0.0.1:8011", use_reloader=False)
