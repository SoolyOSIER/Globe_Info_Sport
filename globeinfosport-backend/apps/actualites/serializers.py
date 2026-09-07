from __future__ import annotations

from rest_framework import serializers

from apps.comptes.serializers import UtilisateurSerializer

from .models import Article, Categorie, ChiffreCle, Citation, Tag, Video


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ["id", "nom", "slug"]
        read_only_fields = ["id"]


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
    slug = serializers.SlugField(required=False, allow_blank=True, max_length=270)

    class Meta:
        model = Article
        fields = [
            "id",
            "titre",
            "slug",
            "chapo",
            "contenu",
            "image_une",
            "categorie",
            "tags",
            "statut",
            "a_la_une",
            "source",
        ]
        read_only_fields = ["id"]

    def validate_statut(self, value: str) -> str:
        if value == Article.Statut.PUBLIE:
            raise serializers.ValidationError(
                "Utilisez l'action de publication pour publier un article."
            )
        return value


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
            "chapo",
            "image_une",
            "categorie",
            "tags",
            "a_la_une",
            "source",
            "date_publication",
        ]


class ArticlePublicDetailSerializer(ArticlePublicListSerializer):
    """Détail public avec contenu, vidéos et citations associés."""

    videos = VideoSerializer(many=True, read_only=True)
    citations = CitationSerializer(many=True, read_only=True)

    class Meta(ArticlePublicListSerializer.Meta):
        fields = [
            *ArticlePublicListSerializer.Meta.fields,
            "contenu",
            "videos",
            "citations",
        ]


class ChiffreCleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChiffreCle
        fields = ["id", "libelle", "valeur", "icone", "ordre"]
        read_only_fields = fields
