"""Données propres aux interactions et éléments transverses de la vitrine."""

from __future__ import annotations

import secrets

from django.db import models

from apps.core.models import TimeStampedModel


def generer_token_desabonnement() -> str:
    """Crée un jeton opaque, sûr et compatible avec la longueur du champ."""

    return secrets.token_urlsafe(32)[:64]


class MessageContact(TimeStampedModel):
    """Message laissé via le formulaire public de contact."""

    nom = models.CharField(max_length=150)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    traite = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "message de contact"
        verbose_name_plural = "messages de contact"

    def __str__(self) -> str:
        return f"{self.nom} — {self.sujet}"


class AbonneNewsletter(TimeStampedModel):
    """Adresse inscrite à la newsletter, avec opt-out non devinable."""

    email = models.EmailField(unique=True)
    actif = models.BooleanField(default=True)
    token_desabonnement = models.CharField(
        max_length=64,
        unique=True,
        default=generer_token_desabonnement,
        editable=False,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "abonné newsletter"
        verbose_name_plural = "abonnés newsletter"

    def __str__(self) -> str:
        return self.email


class Partenaire(models.Model):
    """Partenaire affiché dans le footer du site public."""

    nom = models.CharField(max_length=150)
    logo = models.ImageField(upload_to="partenaires/")
    url = models.URLField(blank=True)
    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "partenaire"
        verbose_name_plural = "partenaires"

    def __str__(self) -> str:
        return self.nom


class FAQ(models.Model):
    """Question-réponse de la page Contact."""

    question = models.CharField(max_length=255)
    reponse = models.TextField()
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "question"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self) -> str:
        return self.question


class PageContenu(TimeStampedModel):
    """A short editable public content block used by the home page.

    The initial HTML contains editorial sections such as the history and
    infrastructure.  Keeping them in a keyed model lets editors update these
    texts without deploying the public SPA.
    """

    cle = models.SlugField(unique=True, max_length=80)
    titre = models.CharField(max_length=180)
    contenu = models.TextField()
    image = models.ImageField(upload_to="pages/", null=True, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["cle"]
        verbose_name = "contenu de page"
        verbose_name_plural = "contenus de pages"

    def __str__(self) -> str:
        return self.titre
