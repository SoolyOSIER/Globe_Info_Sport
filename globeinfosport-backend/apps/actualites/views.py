from __future__ import annotations

from django.db.models import F, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.permissions import IsEditeurOuPlus, IsRedacteurOuPlus, has_minimum_role

from .filters import ArticleFilter
from .models import ActualiteSyndiquee, Article, Categorie, ChiffreCle, Citation, FluxSyndication, Tag, Video
from .serializers import (
    ArticleCreateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    ArticlePublicDetailSerializer,
    ArticlePublicListSerializer,
    ActualiteSyndiqueePublicSerializer,
    CategoriePublicSerializer,
    CategorieSerializer,
    ChiffreCleSerializer,
    CitationSerializer,
    TagSerializer,
    VideoSerializer,
    FluxSyndicationSerializer,
)
from .tasks import synchroniser_flux_rss


class ArticleViewSet(viewsets.ModelViewSet):
    """Cycle de vie des articles : brouillon, validation, publication et archive."""

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ["titre", "chapo", "contenu"]
    ordering_fields = ["date_publication", "created_at", "updated_at", "titre"]
    ordering = ["-date_publication", "-created_at"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        if getattr(self, "swagger_fake_view", False):
            return Article.objects.none()
        queryset = (
            Article.objects.select_related("categorie", "auteur", "auteur__role_redaction")
            .prefetch_related("tags", "videos", "citations")
            .all()
        )
        user = self.request.user
        if not has_minimum_role(user, "EDITEUR_EN_CHEF"):
            return queryset.filter(Q(statut=Article.Statut.PUBLIE) | Q(auteur=user))
        return queryset

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {"publier", "destroy"}:
            return [IsEditeurOuPlus()]
        return [IsRedacteurOuPlus()]

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "list":
            return ArticleListSerializer
        if self.action in {"create", "update", "partial_update"}:
            return ArticleCreateSerializer
        return ArticleDetailSerializer

    def perform_create(self, serializer) -> None:  # type: ignore[no-untyped-def]
        serializer.save(auteur=self.request.user, statut=Article.Statut.BROUILLON)

    def perform_update(self, serializer) -> None:  # type: ignore[no-untyped-def]
        if (
            serializer.instance.statut == Article.Statut.PUBLIE
            and not has_minimum_role(self.request.user, "EDITEUR_EN_CHEF")
        ):
            raise PermissionDenied(
                "Seul un éditeur en chef peut modifier un article publié."
            )
        serializer.save()

    def retrieve(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        article = self.get_object()
        Article.objects.filter(pk=article.pk).update(compteur_vues=F("compteur_vues") + 1)
        article.refresh_from_db(fields=["compteur_vues"])
        return Response(self.get_serializer(article).data)

    @action(detail=True, methods=["post"])
    def publier(self, request, pk=None):  # type: ignore[no-untyped-def]
        article = self.get_object()
        article.statut = Article.Statut.PUBLIE
        article.date_publication = timezone.now()
        article.save(update_fields=["statut", "date_publication", "updated_at"])
        return Response(ArticleDetailSerializer(article, context={"request": request}).data)


class EditorialReferenceViewSet(viewsets.ModelViewSet):
    """Référentiels éditoriaux lisibles par la rédaction et modifiables par l'éditeur."""

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {"list", "retrieve"}:
            return [IsRedacteurOuPlus()]
        return [IsEditeurOuPlus()]


class CategorieViewSet(EditorialReferenceViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    search_fields = ["nom", "slug"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["nom"]


class TagViewSet(EditorialReferenceViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ["nom", "slug"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["nom"]


class VideoViewSet(EditorialReferenceViewSet):
    queryset = Video.objects.select_related("article_lie").all()
    serializer_class = VideoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["a_la_une", "article_lie"]
    search_fields = ["titre"]
    ordering_fields = ["ordre", "created_at"]


class CitationViewSet(EditorialReferenceViewSet):
    queryset = Citation.objects.select_related("article_lie").all()
    serializer_class = CitationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["article_lie"]
    search_fields = ["auteur_nom", "auteur_fonction", "texte"]
    ordering_fields = ["ordre", "created_at"]


class FluxSyndicationViewSet(viewsets.ModelViewSet):
    queryset = FluxSyndication.objects.select_related("categorie").all()
    serializer_class = FluxSyndicationSerializer
    permission_classes = [IsEditeurOuPlus]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["actif", "categorie"]
    search_fields = ["nom", "url"]
    ordering_fields = ["nom", "dernier_import"]

    @action(detail=False, methods=["post"])
    def synchroniser(self, request):  # type: ignore[no-untyped-def]
        task = synchroniser_flux_rss.delay()
        return Response({"detail": "Synchronisation lancée.", "task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class ChiffreCleListView(ListAPIView):
    """Lecture seule au back-office; les tâches Celery alimentent ces valeurs."""

    queryset = ChiffreCle.objects.all()
    serializer_class = ChiffreCleSerializer
    permission_classes = [IsRedacteurOuPlus]


class ArticlePublicListView(ListAPIView):
    """Liste publique, filtrable et exclusivement composée d'articles publiés."""

    serializer_class = ArticlePublicListSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ["titre", "chapo"]
    ordering_fields = ["date_publication", "titre"]
    ordering = ["-date_publication"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Article.objects.filter(statut=Article.Statut.PUBLIE)
            .select_related("categorie")
            .prefetch_related("tags")
        )


class CategoriePublicListView(ListAPIView):
    """Référentiel léger des rubriques proposées aux lecteurs."""

    queryset = Categorie.objects.all()
    serializer_class = CategoriePublicSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nom"]
    ordering_fields = ["nom"]
    ordering = ["nom"]


class ArticlePublicDetailView(RetrieveAPIView):
    """Détail public d'un article publié, identifié par son slug."""

    serializer_class = ArticlePublicDetailSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    lookup_field = "slug"

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Article.objects.filter(statut=Article.Statut.PUBLIE)
            .select_related("categorie")
            .prefetch_related("tags", "videos", "citations")
        )

    def retrieve(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        article = self.get_object()
        Article.objects.filter(pk=article.pk).update(compteur_vues=F("compteur_vues") + 1)
        return Response(self.get_serializer(article).data, status=status.HTTP_200_OK)


class ChiffreClePublicListView(ListAPIView):
    """Expose les indicateurs de la page Actualités sans workflow interne."""

    queryset = ChiffreCle.objects.all()
    serializer_class = ChiffreCleSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"


class ActualiteSyndiqueePublicListView(ListAPIView):
    queryset = ActualiteSyndiquee.objects.select_related("flux", "flux__categorie").all()
    serializer_class = ActualiteSyndiqueePublicSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["flux", "flux__categorie"]
    search_fields = ["titre", "resume", "flux__nom"]
    ordering_fields = ["date_source", "created_at"]
    ordering = ["-date_source", "-created_at"]


class VideoPublicListView(ListAPIView):
    """Featured and article-related videos without editorial fields."""

    queryset = Video.objects.select_related("article_lie").all()
    serializer_class = VideoSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["a_la_une", "article_lie"]
    ordering_fields = ["ordre", "created_at"]
    ordering = ["ordre", "-created_at"]


class CitationPublicListView(ListAPIView):
    """Quotes presented on the news page and article pages."""

    queryset = Citation.objects.select_related("article_lie").all()
    serializer_class = CitationSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["article_lie"]
    ordering_fields = ["ordre", "created_at"]
    ordering = ["ordre", "-created_at"]
