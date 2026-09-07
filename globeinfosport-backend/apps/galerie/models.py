"""Modèles de galerie photo, organisés par album ou événement."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedModel


class AlbumGalerie(TimeStampedModel):
    titre = models.CharField(max_length=150)
    match_lie = models.ForeignKey(
        "competitions.Match",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="albums",
    )
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at", "titre"]
        verbose_name = "album galerie"
        verbose_name_plural = "albums galerie"

    def __str__(self) -> str:
        return self.titre


class ImageGalerie(TimeStampedModel):
    album = models.ForeignKey(
        AlbumGalerie, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="galerie/")
    legende = models.CharField(max_length=200, blank=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "-created_at"]
        indexes = [models.Index(fields=["album", "ordre"])]
        verbose_name = "image galerie"
        verbose_name_plural = "images galerie"

    def __str__(self) -> str:
        return self.legende or f"Image {self.pk} — {self.album}"
