"""Modèles du calendrier, classement et statistiques de compétition."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class Competition(models.Model):
    """Une compétition suivie par la rédaction."""

    class Type(models.TextChoices):
        CHAMPIONNAT_NATIONAL = "CHAMPIONNAT_NATIONAL", "Championnat National"
        ELIMINATOIRES_CDM = "ELIMINATOIRES_CDM", "Éliminatoires Coupe du Monde"
        LIGUE_NATIONS = "LIGUE_NATIONS", "Ligue des Nations CONCACAF"
        AUTRE = "AUTRE", "Autre"

    nom = models.CharField(max_length=150)
    type = models.CharField(max_length=30, choices=Type.choices)
    saison = models.CharField(max_length=20, help_text='Ex. « 2025-2026 ».')
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["-actif", "-saison", "nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["nom", "type", "saison"],
                name="competition_nom_type_saison_unique",
            )
        ]

    def __str__(self) -> str:
        return f"{self.nom} ({self.saison})"


class Club(TimeStampedModel):
    """Un club local participant notamment au Championnat National."""

    nom = models.CharField(max_length=150, unique=True)
    ville = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to="clubs/", null=True, blank=True)
    stade = models.CharField(max_length=150, blank=True)
    fondation = models.PositiveIntegerField(null=True, blank=True)
    palmares = models.TextField(blank=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom


class ClassementLigne(TimeStampedModel):
    """Ligne calculée du classement d'une compétition.

    Ces champs ne doivent pas être modifiés manuellement : les services de
    l'application les reconstruisent depuis les matchs terminés.
    """

    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="classement"
    )
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="classements"
    )
    matchs_joues = models.PositiveIntegerField(default=0)
    victoires = models.PositiveIntegerField(default=0)
    nuls = models.PositiveIntegerField(default=0)
    defaites = models.PositiveIntegerField(default=0)
    buts_pour = models.PositiveIntegerField(default=0)
    buts_contre = models.PositiveIntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        ordering = ["-points", "-buts_pour", "-buts_contre", "club__nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["competition", "club"],
                name="classement_ligne_competition_club_unique",
            )
        ]
        verbose_name = "ligne de classement"
        verbose_name_plural = "lignes de classement"

    @property
    def difference_buts(self) -> int:
        """Retourne la différence de buts, dérivée des deux totaux."""

        return self.buts_pour - self.buts_contre

    def __str__(self) -> str:
        return f"{self.competition} — {self.club}"


class Match(TimeStampedModel):
    """Un match du calendrier, à venir, en direct, terminé ou reporté."""

    class Statut(models.TextChoices):
        A_VENIR = "A_VENIR", "À venir"
        EN_COURS = "EN_COURS", "En cours"
        TERMINE = "TERMINE", "Terminé"
        REPORTE = "REPORTE", "Reporté"

    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="matchs"
    )
    club_domicile = models.ForeignKey(
        Club, on_delete=models.PROTECT, related_name="matchs_domicile"
    )
    club_exterieur = models.ForeignKey(
        Club,
        on_delete=models.PROTECT,
        related_name="matchs_exterieur",
        null=True,
        blank=True,
    )
    adversaire_texte = models.CharField(max_length=150, blank=True)
    date_heure = models.DateTimeField()
    lieu = models.CharField(max_length=200, blank=True)
    diffusion_tv = models.CharField(max_length=150, blank=True)
    score_domicile = models.PositiveSmallIntegerField(null=True, blank=True)
    score_exterieur = models.PositiveSmallIntegerField(null=True, blank=True)
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.A_VENIR
    )
    resume = models.TextField(blank=True)

    class Meta:
        ordering = ["date_heure"]
        indexes = [
            models.Index(fields=["competition", "statut", "date_heure"]),
            models.Index(fields=["statut", "date_heure"]),
        ]

    def clean(self) -> None:
        """Garantit qu'un match a un adversaire et un score cohérent."""

        errors: dict[str, str] = {}
        if self.club_exterieur_id and self.club_exterieur_id == self.club_domicile_id:
            errors["club_exterieur"] = (
                "Le club extérieur doit être différent du club domicile."
            )
        if not self.club_exterieur_id and not self.adversaire_texte.strip():
            errors["adversaire_texte"] = (
                "Indiquez un adversaire texte si aucun club extérieur n'est choisi."
            )
        one_score_is_missing = (
            self.score_domicile is None
        ) != (self.score_exterieur is None)
        if one_score_is_missing:
            errors["score_domicile"] = (
                "Les deux scores doivent être renseignés ensemble."
            )
        if self.statut == self.Statut.TERMINE and (
            self.score_domicile is None or self.score_exterieur is None
        ):
            errors["statut"] = "Un match terminé doit avoir ses deux scores."
        if errors:
            raise ValidationError(errors)

    @property
    def adversaire(self) -> str:
        """Nom affichable de l'adversaire extérieur."""

        return str(self.club_exterieur or self.adversaire_texte)

    def __str__(self) -> str:
        return (
            f"{self.club_domicile} vs {self.adversaire} — "
            f"{self.date_heure:%d/%m/%Y}"
        )


class ButeurMatch(models.Model):
    """Un but déclaré par la rédaction pour un match donné."""

    class TypeBut(models.TextChoices):
        BUT = "BUT", "But"
        PENALTY = "PENALTY", "Penalty"
        CSC = "CSC", "Contre son camp"

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="buteurs")
    joueur = models.ForeignKey("joueurs.Joueur", on_delete=models.CASCADE)
    passeur = models.ForeignKey(
        "joueurs.Joueur",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="passes_match",
    )
    minute = models.PositiveSmallIntegerField()
    type_but = models.CharField(
        max_length=15, choices=TypeBut.choices, default=TypeBut.BUT
    )

    class Meta:
        ordering = ["minute", "pk"]
        indexes = [models.Index(fields=["match", "joueur"])]
        verbose_name = "buteur du match"
        verbose_name_plural = "buteurs des matchs"

    def clean(self) -> None:
        if self.minute > 130:
            raise ValidationError({"minute": "La minute doit être comprise entre 0 et 130."})

    def __str__(self) -> str:
        return f"{self.joueur} ({self.minute}')"


class ParticipationMatch(models.Model):
    """Feuille de match facultative pour les statistiques non déductibles.

    Les buteurs produisent les buts. Les apparitions, cartons et clean sheets
    doivent être saisis explicitement : ils ne peuvent être inventés à partir
    d'un simple score final.
    """

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="participations")
    joueur = models.ForeignKey(
        "joueurs.Joueur", on_delete=models.CASCADE, related_name="participations_match"
    )
    titulaire = models.BooleanField(default=False)
    cartons_jaunes = models.PositiveSmallIntegerField(default=0)
    carton_rouge = models.BooleanField(default=False)
    clean_sheet = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["match", "joueur"],
                name="participation_match_joueur_unique",
            )
        ]

    def __str__(self) -> str:
        return f"{self.joueur} — {self.match}"


class StatistiqueJoueur(TimeStampedModel):
    """Statistiques cumulées, reconstruites par compétition et joueur."""

    joueur = models.ForeignKey(
        "joueurs.Joueur", on_delete=models.CASCADE, related_name="statistiques"
    )
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="statistiques_joueurs"
    )
    matchs_joues = models.PositiveIntegerField(default=0)
    buts = models.PositiveIntegerField(default=0)
    passes_decisives = models.PositiveIntegerField(default=0)
    cartons_jaunes = models.PositiveIntegerField(default=0)
    cartons_rouges = models.PositiveIntegerField(default=0)
    clean_sheets = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-buts", "-passes_decisives", "-clean_sheets", "joueur__nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["joueur", "competition"],
                name="statistique_joueur_competition_unique",
            )
        ]
        verbose_name = "statistique joueur"
        verbose_name_plural = "statistiques joueurs"

    def __str__(self) -> str:
        return f"{self.joueur} — {self.competition}"
