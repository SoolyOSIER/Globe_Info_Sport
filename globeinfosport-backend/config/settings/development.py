"""Development-only settings."""

from .base import *  # noqa: F403

DEBUG = True
DATABASES = {
    "default": env.db(  # noqa: F405
        "DATABASE_URL",
        default="postgres://globeinfosport:globeinfosport@localhost:5432/globeinfosport",
    )
}
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# En l'absence de Redis local, les tâches déclenchées par les formulaires
# restent testables. En Docker, CELERY_TASK_ALWAYS_EAGER=False les délègue au
# worker Celery, comme en production.
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=True)  # noqa: F405
CELERY_TASK_EAGER_PROPAGATES = False
