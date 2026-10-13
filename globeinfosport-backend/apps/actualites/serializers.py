from __future__ import annotations
import json

from rest_framework import serializers

from apps.comptes.serializers import UtilisateurSerializer

from .models import Sport, Pays, Selection, RevisionArticle, CommentaireInterne
from .models import ActualiteSyndiquee, Article, Categorie, ChiffreCle, Citation, FluxSyndication, Tag, Video


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ["id", "nom", "slug"]
        read_only_fields = ["id"]


class CategoriePublicSerializer(CategorieSerializer):
    """Catégorie éditoriale exposée aux filtres de la vitrine."""


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "nom", "slug"]
        read_only_fields = ["id"]


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            "id",
            "titre",
            "url_embed",
            "article_lie",
            "a_la_une",
            "ordre",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citation
        fields = [
            "id",
            "auteur_nom",
            "auteur_fonction",
            "photo",
            "texte",
            "article_lie",
            "ordre",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ArticleListSerializer(serializers.ModelSerializer):
    """Version légère pour les tableaux rédactionnels et aperçus."""

    categorie = CategorieSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    auteur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "titre",
            "slug",
            "sport", "pays", "competitions", "clubs", "athletes", "selections", "breaking", "recommande", "sponsorise", "titre_seo", "description_seo", "legende_image", "galerie",
            "chapo",
            "image_une",
            "categorie",
            "tags",
            "auteur",
            "statut",
            "a_la_une",
            "date_publication",
            "compteur_vues",
            "created_at",
            "updated_at",
        ]


class ArticleDetailSerializer(ArticleListSerializer):
    """Version complète d'un article, avec les contenus liés."""

    videos = VideoSerializer(many=True, read_only=True)
    citations = CitationSerializer(many=True, read_only=True)

    class Meta(ArticleListSerializer.Meta):
        fields = [
            *ArticleListSerializer.Meta.fields,
            "contenu",
            "source",
            "videos",
            "citations",
        ]


class ArticleCreateSerializer(serializers.ModelSerializer):
    """Écriture d'un article; l'auteur est systématiquement le demandeur."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False,
    )
    video_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        write_only=True,
    )
    slug = serializers.SlugField(required=False, allow_blank=True, max_length=270)

    def to_internal_value(self, data):
        # A JSON envelope preserves empty lists when an image is uploaded.
        if "payload" in data:
            try:
                payload = json.loads(data["payload"])
            except (TypeError, ValueError):
                raise serializers.ValidationError({"payload": "JSON invalide."})
            if not isinstance(payload, dict):
                raise serializers.ValidationError({"payload": "Un objet JSON est requis."})
            if "image_une" in data:
                payload["image_une"] = data["image_une"]
            data = payload
        return super().to_internal_value(data)

    class Meta:
        model = Article
        fields = [
            "id",
            "titre",
            "slug",
            "sport", "pays", "competitions", "clubs", "athletes", "selections", "breaking", "recommande", "sponsorise", "titre_seo", "description_seo", "legende_image", "galerie",
            "chapo",
            "contenu",
            "image_une",
            "categorie",
            "tags",
            "statut",
            "a_la_une",
            "source",
            "video_urls",
        ]
        read_only_fields = ["id"]

    def validate_slug(self, value):
        if value and Article.objects.filter(slug=value).exclude(pk=getattr(self.instance, "pk", None)).exists():
            raise serializers.ValidationError("Ce slug existe déjà.")
        return value

    def validate_statut(self, value: str) -> str:
        if self.instance is not None or value != Article.Statut.BROUILLON:
            raise serializers.ValidationError(
                "Utilisez l'action de publication pour publier un article."
            )
        return value

    def _synchroniser_videos(self, article: Article, urls: list[str] | None) -> None:
        if urls is None:
            return
        article.videos.all().delete()
        Video.objects.bulk_create(
            [
                Video(
                    titre=f"Vidéo liée · {index + 1}",
                    url_embed=url,
                    article_lie=article,
                    ordre=index,
                )
                for index, url in enumerate(urls)
            ]
        )

    def create(self, validated_data):
        urls = validated_data.pop("video_urls", None)
        article = super().create(validated_data)
        self._synchroniser_videos(article, urls)
        return article

    def update(self, instance, validated_data):
        urls = validated_data.pop("video_urls", None)
        article = super().update(instance, validated_data)
        self._synchroniser_videos(article, urls)
        return article


class ArticlePublicListSerializer(serializers.ModelSerializer):
    """Projection publique sans champs de workflow interne."""

    categorie = CategorieSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "titre",
            "slug",
            "sport", "pays", "competitions", "clubs", "athletes", "selections", "breaking", "recommande", "sponsorise", "titre_seo", "description_seo", "legende_image", "galerie",
            "chapo",
            "image_une",
            "categorie",
            "tags",
            "a_la_une",
            "source",
            "date_publication",
        ]


class ArticlePublicDetailSerializer(ArticlePublicListSerializer):
    auteur_nom = serializers.CharField(source="auteur.get_full_name", read_only=True)
    galerie_detail = serializers.SerializerMethodField()
    precedent = serializers.SerializerMethodField()
    suivant = serializers.SerializerMethodField()

    def adjacent(self, obj, newer):
        from django.db.models import Q
        from django.utils import timezone
        articles = Article.objects.filter(statut=Article.Statut.PUBLIE, date_publication__lte=timezone.now())
        if newer:
            articles = articles.filter(Q(date_publication__gt=obj.date_publication) | Q(date_publication=obj.date_publication, pk__gt=obj.pk)).order_by("date_publication", "pk")
        else:
            articles = articles.filter(Q(date_publication__lt=obj.date_publication) | Q(date_publication=obj.date_publication, pk__lt=obj.pk)).order_by("-date_publication", "-pk")
        return articles.values("titre", "slug").first()

    def get_precedent(self, obj):
        return self.adjacent(obj, False)

    def get_suivant(self, obj):
        return self.adjacent(obj, True)

    def get_galerie_detail(self, obj):
        from apps.galerie.serializers import ImageGalerieSerializer
        return ImageGalerieSerializer(obj.galerie.all(), many=True, context=self.context).data

    """Détail public avec contenu, vidéos et citations associés."""

    videos = VideoSerializer(many=True, read_only=True)
    citations = CitationSerializer(many=True, read_only=True)

    class Meta(ArticlePublicListSerializer.Meta):
        fields = [
            *ArticlePublicListSerializer.Meta.fields,
            "auteur_nom", "updated_at", "galerie_detail", "precedent", "suivant",
            "contenu",
            "videos",
            "citations",
        ]


class ChiffreCleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChiffreCle
        fields = ["id", "libelle", "valeur", "icone", "ordre"]
        read_only_fields = fields


class FluxSyndicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FluxSyndication
        fields = ["id", "nom", "url", "categorie", "actif", "dernier_import", "dernier_statut", "created_at", "updated_at"]
        read_only_fields = ["id", "dernier_import", "dernier_statut", "created_at", "updated_at"]


class ActualiteSyndiqueePublicSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="flux.nom", read_only=True)
    categorie = CategoriePublicSerializer(source="flux.categorie", read_only=True)

    class Meta:
        model = ActualiteSyndiquee
        fields = ["id", "titre", "url", "resume", "image_url", "date_source", "source", "categorie"]


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ["id", "nom", "slug"]


class PaysSerializer(serializers.ModelSerializer):
    def validate_code(self, value):
        if len(value) != 2 or not value.isalpha():
            raise serializers.ValidationError("Utilisez un code pays de deux lettres.")
        return value.upper()

    class Meta:
        model = Pays
        fields = ["id", "nom", "code", "region"]


class SelectionSerializer(serializers.ModelSerializer):
    pays_detail = PaysSerializer(source="pays", read_only=True)
    sport_detail = SportSerializer(source="sport", read_only=True)
    joueurs_detail = serializers.SerializerMethodField()
    competitions_detail = serializers.SerializerMethodField()

    def get_joueurs_detail(self, obj):
        from apps.joueurs.serializers import JoueurListSerializer

        return JoueurListSerializer(obj.joueurs.all(), many=True, context=self.context).data

    def get_competitions_detail(self, obj):
        from apps.competitions.serializers import CompetitionPublicSerializer

        return CompetitionPublicSerializer(
            obj.competitions.all(), many=True, context=self.context
        ).data

    class Meta:
        model = Selection
        fields = [
            "id",
            "nom",
            "pays",
            "pays_detail",
            "sport",
            "sport_detail",
            "logo",
            "entraineur",
            "histoire",
            "joueurs",
            "joueurs_detail",
            "competitions",
            "competitions_detail",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RevisionSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.CharField(source="auteur.nom", read_only=True)
    class Meta:
        model = RevisionArticle
        fields = ["id", "auteur_nom", "action", "donnees", "created_at"]


class CommentaireSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.CharField(source="auteur.nom", read_only=True)
    class Meta:
        model = CommentaireInterne
        fields = ["id", "auteur_nom", "texte", "created_at"]
        read_only_fields = ["id", "created_at"]
