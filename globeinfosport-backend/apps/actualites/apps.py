from django.apps import AppConfig


class ActualitesConfig(AppConfig):
    """Configuration de l'application éditoriale."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.actualites"
    verbose_name = "Actualités"

    def ready(self) -> None:
        from . import signals  # noqa: F401
