"""Stockage média S3-compatible utilisé uniquement en production."""

try:
    from storages.backends.s3boto3 import S3Boto3Storage
except ImportError:  # pragma: no cover - django-storages est une dépendance prod
    from django.core.files.storage import FileSystemStorage

    class MediaStorage(FileSystemStorage):
        """Fallback local explicite lorsque django-storages est absent."""

        pass
else:

    class MediaStorage(S3Boto3Storage):
        """Stockage média sans écrasement de fichiers existants."""

        file_overwrite = False
