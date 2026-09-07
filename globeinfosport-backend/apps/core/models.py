from django.db import models


class TimeStampedModel(models.Model):
    """Base abstraite ajoutant les dates de création et de mise à jour."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
