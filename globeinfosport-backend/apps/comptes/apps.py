from django.apps import AppConfig


class ComptesConfig(AppConfig):
    """Configuration des comptes de la rédaction."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.comptes"
    verbose_name = "Comptes de la rédaction"

    def ready(self) -> None:
        # L'import tardif évite l'enregistrement des signaux avant le chargement
        # complet du registre des applications.
        from . import signals  # noqa: F401
