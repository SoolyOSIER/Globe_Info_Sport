from django.apps import AppConfig


class CompetitionsConfig(AppConfig):
    """Configuration de l'application compétitions."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.competitions"
    verbose_name = "Compétitions"

    def ready(self) -> None:
        # L'import est volontairement différé pour que le registre Django soit prêt.
        from . import signals  # noqa: F401

