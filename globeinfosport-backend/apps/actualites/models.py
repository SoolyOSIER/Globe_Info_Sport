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
        PROGRAMME = "PROGRAMME", "Programmé"
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
    sport = models.ForeignKey("Sport", null=True, blank=True, on_delete=models.PROTECT)
    pays = models.ManyToManyField("Pays", blank=True, related_name="articles")
    competitions = models.ManyToManyField("competitions.Competition", blank=True, related_name="articles")
    clubs = models.ManyToManyField("competitions.Club", blank=True, related_name="articles")
    athletes = models.ManyToManyField("joueurs.Joueur", blank=True, related_name="articles")
    selections = models.ManyToManyField("Selection", blank=True, related_name="articles")
    breaking = models.BooleanField(default=False)
    recommande = models.BooleanField(default=False)
    sponsorise = models.BooleanField(default=False)
    titre_seo = models.CharField(max_length=250, blank=True)
    description_seo = models.CharField(max_length=320, blank=True)
    legende_image = models.CharField(max_length=300, blank=True)
    galerie = models.ManyToManyField("galerie.ImageGalerie", blank=True, related_name="articles")

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


class Sport(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _build_unique_slug(self, self.nom, "sport")
        super().save(*args, **kwargs)


class Pays(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)
    region = models.CharField(max_length=40, choices=[(v, v) for v in [
        "Amérique du Nord", "Amérique centrale", "Caraïbes", "Amérique du Sud",
        "Europe", "Afrique", "Asie", "Océanie",
    ]])

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Selection(TimeStampedModel):
    nom = models.CharField(max_length=150)
    pays = models.ForeignKey(Pays, on_delete=models.PROTECT)
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
    logo = models.ImageField(upload_to="selections/", blank=True, null=True)
    entraineur = models.CharField(max_length=150, blank=True)
    histoire = models.TextField(blank=True)
    joueurs = models.ManyToManyField("joueurs.Joueur", blank=True)
    competitions = models.ManyToManyField("competitions.Competition", blank=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class RevisionArticle(TimeStampedModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="revisions")
    auteur = models.ForeignKey("comptes.Utilisateur", null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=40)
    donnees = models.JSONField(default=dict)

    class Meta:
        ordering = ["-created_at", "-pk"]


class CommentaireInterne(TimeStampedModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="commentaires_internes")
    auteur = models.ForeignKey("comptes.Utilisateur", null=True, on_delete=models.SET_NULL)
    texte = models.TextField(max_length=5000)

    class Meta:
        ordering = ["created_at"]


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


class FluxSyndication(TimeStampedModel):
    """Flux RSS autorisé, géré par la rédaction et non par scraping."""

    nom = models.CharField(max_length=120)
    url = models.URLField(unique=True)
    categorie = models.ForeignKey(
        Categorie, null=True, blank=True, on_delete=models.SET_NULL, related_name="flux_syndication"
    )
    actif = models.BooleanField(default=True)
    dernier_import = models.DateTimeField(null=True, blank=True)
    dernier_statut = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom


class ActualiteSyndiquee(TimeStampedModel):
    """Extrait attribué à sa source, publiable uniquement comme lien externe."""

    flux = models.ForeignKey(FluxSyndication, on_delete=models.CASCADE, related_name="actualites")
    titre = models.CharField(max_length=300)
    url = models.URLField(unique=True)
    resume = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    date_source = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date_source", "-created_at"]
        verbose_name = "actualité syndiquée"
        verbose_name_plural = "actualités syndiquées"

    def __str__(self) -> str:
        return self.titre
