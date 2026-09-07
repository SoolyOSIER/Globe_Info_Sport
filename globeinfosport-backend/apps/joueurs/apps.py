from django.apps import AppConfig


class JoueursConfig(AppConfig):
    """Configuration de l'application joueurs."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.joueurs"
    verbose_name = "Joueurs et légendes"
