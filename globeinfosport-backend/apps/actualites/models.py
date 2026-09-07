from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


def _build_unique_slug(instance: models.Model, value: str, fallback: str) -> str:
    """Construit un slug stable et unique pour les contenus éditoriaux."""

    base_slug = slugify(value) or fallback
    candidate = base_slug
    suffix = 2
    queryset = instance.__class__._default_manager.exclude(pk=instance.pk)
    while queryset.filter(slug=candidate).exists():
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
    return candidate


class Categorie(models.Model):
    """Catégorie de classement des articles."""

    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom

    def save(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        if not self.slug:
            self.slug = _build_unique_slug(self, self.nom, "categorie")
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Mot-clé libre relié à plusieurs articles."""

    nom = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom

    def save(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        if not self.slug:
            self.slug = _build_unique_slug(self, self.nom, "tag")
        super().save(*args, **kwargs)


class Article(TimeStampedModel):
    """Article rédigé dans le back-office et publié sur le site public."""

    class Statut(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon"
        A_VALIDER = "A_VALIDER", "À valider"
        PUBLIE = "PUBLIE", "Publié"
        ARCHIVE = "ARCHIVE", "Archivé"

    titre = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, max_length=270, blank=True)
    chapo = models.CharField(max_length=300)
    contenu = models.TextField()
    image_une = models.ImageField(upload_to="articles/", null=True, blank=True)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,
        related_name="articles",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    auteur = models.ForeignKey(
        "comptes.Utilisateur",
        on_delete=models.PROTECT,
        related_name="articles",
    )
    statut = models.CharField(
        max_length=15,
        default=Statut.BROUILLON,
        choices=Statut.choices,
    )
    a_la_une = models.BooleanField(default=False)
    source = models.CharField(max_length=200, blank=True)
    date_publication = models.DateTimeField(null=True, blank=True)
    compteur_vues = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date_publication", "-created_at"]
        indexes = [
            models.Index(fields=["statut", "-date_publication"]),
            models.Index(fields=["a_la_une", "-date_publication"]),
        ]

    def __str__(self) -> str:
        return self.titre

    def save(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        if not self.slug:
            self.slug = _build_unique_slug(self, self.titre, "article")
        if self.statut == self.Statut.PUBLIE and self.date_publication is None:
            self.date_publication = timezone.now()
        super().save(*args, **kwargs)


class Video(TimeStampedModel):
    """Vidéo mise en avant sur la rubrique Actualités."""

    titre = models.CharField(max_length=200)
    url_embed = models.URLField()
    article_lie = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="videos",
    )
    a_la_une = models.BooleanField(default=False)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "-created_at"]

    def __str__(self) -> str:
        return self.titre


class Citation(TimeStampedModel):
    """Citation d'un acteur du football haïtien."""

    auteur_nom = models.CharField(max_length=150)
    auteur_fonction = models.CharField(max_length=150, blank=True)
    photo = models.ImageField(upload_to="citations/", null=True, blank=True)
    texte = models.TextField()
    article_lie = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citations",
    )
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "-created_at"]

    def __str__(self) -> str:
        return f"{self.auteur_nom} — {self.texte[:50]}"


class ChiffreCle(models.Model):
    """Indicateur de la page Actualités, calculé périodiquement si demandé."""

    libelle = models.CharField(max_length=100)
    valeur = models.CharField(max_length=30)
    icone = models.CharField(max_length=50, blank=True)
    calcule_auto = models.BooleanField(default=True)
    code_calcul = models.CharField(max_length=50, blank=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "chiffre clé"
        verbose_name_plural = "chiffres clés"
        ordering = ["ordre"]

    def __str__(self) -> str:
        return f"{self.libelle} : {self.valeur}"
