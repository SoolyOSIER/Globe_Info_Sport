"""Modèles métier de la rubrique SPI / expatriés."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class ClubEtranger(models.Model):
    """Un club étranger dans lequel évolue un joueur haïtien."""

    nom = models.CharField(max_length=150)
    pays = models.CharField(max_length=100)
    ligue = models.CharField(max_length=150, blank=True)
    logo = models.ImageField(upload_to="clubs_etrangers/", null=True, blank=True)

    class Meta:
        ordering = ["pays", "nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["nom", "pays", "ligue"],
                name="club_etranger_nom_pays_ligue_unique",
            )
        ]
        verbose_name = "club étranger"
        verbose_name_plural = "clubs étrangers"

    def __str__(self) -> str:
        return f"{self.nom} ({self.pays})"


class JoueurExpatrie(TimeStampedModel):
    """Extension internationale d'une fiche ``Joueur`` unique."""

    class Statut(models.TextChoices):
        ACTIF = "ACTIF", "Actif"
        PRETE = "PRETE", "Prêté"
        BLESSE = "BLESSE", "Blessé"
        LIBRE = "LIBRE", "Libre"

    joueur = models.OneToOneField(
        "joueurs.Joueur", on_delete=models.CASCADE, related_name="fiche_expatrie"
    )
    club_etranger = models.ForeignKey(
        ClubEtranger, on_delete=models.PROTECT, related_name="joueurs_expatries"
    )
    date_arrivee = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.ACTIF)
    en_vedette = models.BooleanField(default=False)

    class Meta:
        ordering = ["-en_vedette", "joueur__nom", "joueur__prenom"]
        verbose_name = "joueur expatrié"
        verbose_name_plural = "joueurs expatriés"

    def __str__(self) -> str:
        return f"{self.joueur} — {self.club_etranger}"


class Transfert(TimeStampedModel):
    """Mouvement de carrière d'un joueur haïtien."""

    class TypeTransfert(models.TextChoices):
        DEFINITIF = "DEFINITIF", "Transfert définitif"
        PRET = "PRET", "Prêt"

    joueur = models.ForeignKey(
        "joueurs.Joueur", on_delete=models.CASCADE, related_name="transferts"
    )
    club_origine = models.CharField(max_length=150)
    club_destination = models.CharField(max_length=150)
    date_transfert = models.DateField()
    type_transfert = models.CharField(max_length=15, choices=TypeTransfert.choices)
    montant = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-date_transfert", "-created_at"]
        verbose_name = "transfert"
        verbose_name_plural = "transferts"

    def clean(self) -> None:
        if self.club_origine.strip().casefold() == self.club_destination.strip().casefold():
            raise ValidationError(
                {"club_destination": "Le club de destination doit être différent du club d'origine."}
            )

    def __str__(self) -> str:
        return f"{self.joueur} : {self.club_origine} → {self.club_destination}"
