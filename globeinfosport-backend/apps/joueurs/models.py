from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class Poste(models.Model):
    """Poste de jeu normalisé pour les fiches joueurs."""

    nom = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom


class Joueur(TimeStampedModel):
    """Athlète international, réutilisable par les compétitions et expatriés."""

    class PiedFort(models.TextChoices):
        GAUCHE = "GAUCHE", "Gauche"
        DROIT = "DROIT", "Droit"

    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150, blank=True)
    sport = models.ForeignKey("actualites.Sport", null=True, blank=True, on_delete=models.PROTECT)
    pays = models.ForeignKey("actualites.Pays", null=True, blank=True, on_delete=models.PROTECT)
    photo = models.ImageField(upload_to="joueurs/", null=True, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    poste = models.ForeignKey(
        Poste,
        on_delete=models.PROTECT,
        related_name="joueurs",
        null=True,
        blank=True,
    )
    club_actuel = models.CharField(max_length=150, blank=True)
    numero_maillot = models.PositiveSmallIntegerField(null=True, blank=True)
    taille_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    pied_fort = models.CharField(
        max_length=10,
        blank=True,
        choices=PiedFort.choices,
    )
    biographie = models.TextField(blank=True)
    selection_nationale = models.BooleanField(default=True)
    nb_selections = models.PositiveIntegerField(default=0)
    nb_buts_selection = models.PositiveIntegerField(default=0)
    emblematique = models.BooleanField(default=False)

    class Meta:
        verbose_name = "joueur"
        verbose_name_plural = "joueurs"
        ordering = ["nom", "prenom"]
        indexes = [
            models.Index(fields=["selection_nationale", "emblematique"]),
        ]

    def __str__(self) -> str:
        return self.nom_complet

    @property
    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}".strip()

    def clean(self) -> None:
        super().clean()
        errors: dict[str, str] = {}
        if self.numero_maillot is not None and not 1 <= self.numero_maillot <= 99:
            errors["numero_maillot"] = "Le numéro de maillot doit être compris entre 1 et 99."
        if self.taille_cm is not None and not 100 <= self.taille_cm <= 250:
            errors["taille_cm"] = "La taille doit être comprise entre 100 et 250 cm."
        if errors:
            raise ValidationError(errors)


class Legende(TimeStampedModel):
    """Figure historique distincte des joueurs actifs du football haïtien."""

    nom = models.CharField(max_length=150)
    photo = models.ImageField(upload_to="legendes/", null=True, blank=True)
    periode_active = models.CharField(max_length=50, blank=True)
    poste = models.CharField(max_length=50, blank=True)
    biographie = models.TextField()
    exploits = models.TextField(blank=True)
    ordre_affichage = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "légende"
        verbose_name_plural = "légendes"
        ordering = ["ordre_affichage", "nom"]

    def __str__(self) -> str:
        return self.nom
