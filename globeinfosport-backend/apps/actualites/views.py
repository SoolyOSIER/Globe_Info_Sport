from __future__ import annotations

from django.db import transaction
from django.db.models import F, Q
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.permissions import IsEditeurOuPlus, IsRedacteurOuPlus, IsAdministrateur, has_minimum_role

from .models import Sport, Pays, Selection, RevisionArticle
from .serializers import SportSerializer, PaysSerializer, SelectionSerializer, RevisionSerializer, CommentaireSerializer
from .filters import ArticleFilter, SelectionFilter
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
            .prefetch_related("tags", "videos", "citations", "pays", "competitions", "clubs", "athletes", "selections", "galerie")
            .all()
        )
        user = self.request.user
        if not has_minimum_role(user, "EDITEUR_EN_CHEF"):
            return queryset.filter(Q(statut=Article.Statut.PUBLIE) | Q(auteur=user))
        return queryset

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {"publier", "programmer", "archiver", "reprendre", "destroy"}:
            return [IsEditeurOuPlus()]
        return [IsRedacteurOuPlus()]

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "list":
            return ArticleListSerializer
        if self.action in {"create", "update", "partial_update"}:
            return ArticleCreateSerializer
        return ArticleDetailSerializer

    def perform_create(self, serializer) -> None:  # type: ignore[no-untyped-def]
        with transaction.atomic():
            article = serializer.save(auteur=self.request.user, statut=Article.Statut.BROUILLON)
            self.record(article, "creation")

    def check_owner(self, article):
        if not has_minimum_role(self.request.user, "EDITEUR_EN_CHEF"):
            if article.auteur_id != self.request.user.pk or article.statut not in {Article.Statut.BROUILLON, Article.Statut.A_VALIDER}:
                raise PermissionDenied("Vous pouvez modifier uniquement vos brouillons et soumissions.")

    def record(self, article, action_name):
        RevisionArticle.objects.create(article=article, auteur=self.request.user,
            action=action_name, donnees=dict(ArticleDetailSerializer(article, context={"request": self.request}).data))

    def perform_update(self, serializer):
        self.check_owner(serializer.instance)
        with transaction.atomic():
            article = serializer.save()
            article.refresh_from_db()
            self.record(article, "modification")

    @action(detail=True, methods=["post"])
    def soumettre(self, request, pk=None):
        with transaction.atomic():
            article = self.get_queryset().select_for_update().get(pk=self.get_object().pk)
            self.check_owner(article)
            if article.statut != Article.Statut.BROUILLON:
                raise ValidationError("Seul un brouillon peut etre soumis.")
            article.statut = Article.Statut.A_VALIDER
            article.save()
            self.record(article, "soumission")
        return Response(ArticleDetailSerializer(article).data)

    def transition(self, request, target):
        with transaction.atomic():
            article = self.get_queryset().select_for_update().get(pk=self.get_object().pk)
            if target in {Article.Statut.PUBLIE, Article.Statut.PROGRAMME} and not all([article.titre.strip(), article.chapo.strip(), article.contenu.strip()]):
                raise ValidationError("Titre, chapeau et contenu sont requis pour publier.")
            if target == Article.Statut.PROGRAMME:
                try:
                    date = parse_datetime(str(request.data.get("date_publication", "")))
                except ValueError:
                    date = None
                if not date or timezone.is_naive(date) or date <= timezone.now():
                    raise ValidationError({"date_publication": "Indiquez une date future avec fuseau horaire."})
                article.date_publication = date
            elif target == Article.Statut.PUBLIE:
                article.date_publication = timezone.now()
            elif target == Article.Statut.BROUILLON:
                article.date_publication = None
            article.statut = target
            article.save()
            self.record(article, target)
        return Response(ArticleDetailSerializer(article, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def publier(self, request, pk=None):
        return self.transition(request, Article.Statut.PUBLIE)

    @action(detail=True, methods=["post"])
    def programmer(self, request, pk=None):
        return self.transition(request, Article.Statut.PROGRAMME)

    @action(detail=True, methods=["post"])
    def archiver(self, request, pk=None):
        return self.transition(request, Article.Statut.ARCHIVE)

    @action(detail=True, methods=["post"])
    def reprendre(self, request, pk=None):
        return self.transition(request, Article.Statut.BROUILLON)

    @action(detail=True, methods=["get"])
    def historique(self, request, pk=None):
        article = self.get_object()
        self.check_internal_access(article)
        return Response(RevisionSerializer(article.revisions.select_related("auteur")[:100], many=True).data)

    def check_internal_access(self, article):
        if article.auteur_id != self.request.user.pk and not has_minimum_role(self.request.user, "EDITEUR_EN_CHEF"):
            raise PermissionDenied("Cet espace est reserve a l'auteur et aux editeurs.")

    @action(detail=True, methods=["get", "post"])
    def commentaires(self, request, pk=None):
        article = self.get_object()
        self.check_internal_access(article)
        if request.method == "POST":
            serializer = CommentaireSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(article=article, auteur=request.user)
            return Response(serializer.data, status=201)
        return Response(CommentaireSerializer(article.commentaires_internes.select_related("auteur"), many=True).data)


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
    search_fields = ["titre", "chapo", "tags__nom", "sport__nom", "pays__nom", "clubs__nom", "competitions__nom", "athletes__nom", "auteur__nom"]
    ordering_fields = ["date_publication", "titre"]
    ordering = ["-date_publication"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Article.objects.filter(statut=Article.Statut.PUBLIE, date_publication__lte=timezone.now())
            .select_related("categorie", "auteur", "sport")
            .prefetch_related("tags", "pays", "competitions", "clubs", "athletes", "selections", "galerie")
        )

    def filter_queryset(self, queryset):  # type: ignore[no-untyped-def]
        # Les filtres sur tags, pays et relations multiples ne doivent jamais
        # afficher deux fois un même article.
        return super().filter_queryset(queryset).distinct()


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
            Article.objects.filter(statut=Article.Statut.PUBLIE, date_publication__lte=timezone.now())
            .select_related("categorie", "auteur", "sport")
            .prefetch_related("tags", "videos", "citations", "pays", "competitions", "clubs", "athletes", "selections", "galerie")
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

    serializer_class = VideoSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["a_la_une", "article_lie"]
    ordering_fields = ["ordre", "created_at"]
    ordering = ["ordre", "-created_at"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return Video.objects.select_related("article_lie").filter(
            Q(article_lie__isnull=True)
            | Q(
                article_lie__statut=Article.Statut.PUBLIE,
                article_lie__date_publication__lte=timezone.now(),
            )
        )


class CitationPublicListView(ListAPIView):
    """Quotes presented on the news page and article pages."""

    serializer_class = CitationSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["article_lie"]
    ordering_fields = ["ordre", "created_at"]
    ordering = ["ordre", "-created_at"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return Citation.objects.select_related("article_lie").filter(
            Q(article_lie__isnull=True)
            | Q(
                article_lie__statut=Article.Statut.PUBLIE,
                article_lie__date_publication__lte=timezone.now(),
            )
        )


class InternationalReferenceViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nom"]
    ordering_fields = ["nom"]
    ordering = ["nom"]
    def get_permissions(self):
        return [AllowAny()] if self.action in {"list", "retrieve"} else [IsAdministrateur()]


class SportViewSet(InternationalReferenceViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer


class PaysViewSet(InternationalReferenceViewSet):
    queryset = Pays.objects.all()
    serializer_class = PaysSerializer
    filterset_fields = ["region", "code"]


class SelectionViewSet(InternationalReferenceViewSet):
    queryset = Selection.objects.select_related("pays", "sport").prefetch_related("joueurs", "competitions")
    serializer_class = SelectionSerializer
    filterset_class = SelectionFilter
