from django.apps import AppConfig


class VitrineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vitrine"
    verbose_name = "Vitrine publique"

    def ready(self) -> None:
        from . import signals  # noqa: F401

