"""Production-only settings."""

from .base import *  # noqa: F403

DEBUG = False
DATABASES = {"default": env.db("DATABASE_URL")}  # noqa: F405
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
