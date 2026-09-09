"""Vues privées et publiques des compétitions."""

from __future__ import annotations

from django.core.cache import cache
from django.http import FileResponse, Http404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from drf_spectacular.utils import OpenApiTypes, extend_schema

from apps.competitions.consumers import diffuser_score_live
from apps.competitions.filters import (
    ClubFilter,
    CompetitionFilter,
    MatchFilter,
    StatistiqueJoueurFilter,
)
from apps.competitions.models import ClassementLigne, Club, Competition, Match, ParcoursClub, StatistiqueJoueur
from apps.competitions.serializers import (
    ClassementLigneSerializer,
    ClassementPublicSerializer,
    ClubPublicSerializer,
    ClubPublicDetailSerializer,
    ClubSerializer,
    CompetitionPublicSerializer,
    CompetitionSerializer,
    MatchDetailSerializer,
    MatchListSerializer,
    MatchPublicSerializer,
    MatchResultatSerializer,
    ParcoursClubSerializer,
    ScoreDirectSerializer,
    StatistiqueJoueurPublicSerializer,
    StatistiqueJoueurSerializer,
)
from apps.competitions.tasks import build_calendrier_pdf
from apps.core.permissions import IsEditeurOuPlus, IsRedacteurOuPlus
from apps.vitrine.throttles import PublicReadThrottle


class ReadRedacteurWriteEditeurMixin:
    """Autorise la lecture aux rédacteurs et la configuration aux éditeurs."""

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {"list", "retrieve"}:
            return [IsRedacteurOuPlus()]
        return [IsEditeurOuPlus()]


class CompetitionViewSet(ReadRedacteurWriteEditeurMixin, viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CompetitionFilter
    search_fields = ["nom", "saison"]
    ordering_fields = ["nom", "saison", "actif"]


class ClubViewSet(ReadRedacteurWriteEditeurMixin, viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClubFilter
    search_fields = ["nom", "ville", "stade"]
    ordering_fields = ["nom", "ville", "created_at"]


class ParcoursClubViewSet(ReadRedacteurWriteEditeurMixin, viewsets.ModelViewSet):
    queryset = ParcoursClub.objects.select_related("club").all()
    serializer_class = ParcoursClubSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["club", "saison"]
    ordering_fields = ["saison", "ordre", "created_at"]


class ClassementListView(ListAPIView):
    """Classement de back-office, strictement en lecture seule."""

    serializer_class = ClassementLigneSerializer
    permission_classes = [IsRedacteurOuPlus]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return ClassementLigne.objects.filter(
            competition_id=self.kwargs.get("competition_id")
        ).select_related("club", "competition")


class MatchViewSet(viewsets.ModelViewSet):
    """Gestion éditoriale du calendrier et des résultats."""

    queryset = Match.objects.select_related(
        "competition", "club_domicile", "club_exterieur"
    ).prefetch_related("buteurs__joueur", "buteurs__joueur__poste")
    permission_classes = [IsRedacteurOuPlus]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MatchFilter
    ordering_fields = ["date_heure", "created_at", "updated_at"]
    ordering = ["date_heure"]

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "list":
            return MatchListSerializer
        if self.action == "saisir_resultat":
            return MatchResultatSerializer
        if self.action == "mettre_a_jour_score_direct":
            return ScoreDirectSerializer
        return MatchDetailSerializer

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        instance = serializer.save()
        instance.full_clean()

    def perform_update(self, serializer):  # type: ignore[no-untyped-def]
        instance = serializer.save()
        instance.full_clean()

    @action(detail=True, methods=["post"], url_path="saisir-resultat")
    def saisir_resultat(self, request, pk=None):  # type: ignore[no-untyped-def]
        """Enregistre le score final, déclenchant les calculs sportifs."""

        match = self.get_object()
        serializer = MatchResultatSerializer(match, data=request.data)
        serializer.is_valid(raise_exception=True)
        match = serializer.save()
        cache.delete(f"classement:{match.competition_id}")
        cache.delete(f"stats:{match.competition_id}")
        return Response(MatchDetailSerializer(match, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["patch"], url_path="score-direct")
    def mettre_a_jour_score_direct(self, request, pk=None):  # type: ignore[no-untyped-def]
        """Met à jour et diffuse le score d'un match en cours."""

        match = self.get_object()
        serializer = ScoreDirectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        match.score_domicile = serializer.validated_data["score_domicile"]
        match.score_exterieur = serializer.validated_data["score_exterieur"]
        match.statut = Match.Statut.EN_COURS
        match.full_clean()
        match.save(update_fields=["score_domicile", "score_exterieur", "statut", "updated_at"])
        diffuser_score_live(match)
        return Response(MatchDetailSerializer(match, context=self.get_serializer_context()).data)

    @action(
        detail=False,
        methods=["get"],
        url_path="calendrier/telecharger",
        permission_classes=[IsRedacteurOuPlus],
    )
    def telecharger_calendrier(self, request):  # type: ignore[no-untyped-def]
        """Produit immédiatement un PDF exploitable par le back-office."""

        competition_id = request.query_params.get("competition")
        try:
            competition_id_int = int(competition_id) if competition_id else None
        except (TypeError, ValueError):
            return Response(
                {"detail": "Le paramètre competition doit être un entier."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pdf = build_calendrier_pdf(competition_id_int)
        filename = f"calendrier-{timezone.now():%Y%m%d}.pdf"
        return FileResponse(pdf, as_attachment=True, filename=filename)


class StatistiqueJoueurListView(ListAPIView):
    serializer_class = StatistiqueJoueurSerializer
    permission_classes = [IsRedacteurOuPlus]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StatistiqueJoueurFilter
    ordering_fields = ["buts", "passes_decisives", "clean_sheets", "matchs_joues"]
    ordering = ["-buts", "-passes_decisives", "-clean_sheets"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return StatistiqueJoueur.objects.select_related("joueur", "joueur__poste", "competition")


class _PublicReadMixin:
    permission_classes = [AllowAny]
    throttle_classes = [PublicReadThrottle]
    throttle_scope = "public-read"


class CompetitionPublicListView(_PublicReadMixin, ListAPIView):
    queryset = Competition.objects.filter(actif=True)
    serializer_class = CompetitionPublicSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CompetitionFilter
    ordering_fields = ["nom", "saison"]


class ClubPublicListView(_PublicReadMixin, ListAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubPublicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClubFilter
    search_fields = ["nom", "ville"]
    ordering_fields = ["nom", "ville"]


class ClubPublicDetailView(_PublicReadMixin, RetrieveAPIView):
    queryset = Club.objects.prefetch_related("parcours").all()
    serializer_class = ClubPublicDetailSerializer
    lookup_field = "slug"


class ClassementPublicView(_PublicReadMixin, ListAPIView):
    serializer_class = ClassementPublicSerializer

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return ClassementLigne.objects.filter(
            competition_id=self.kwargs.get("competition_id")
        ).select_related("club", "competition")


class MatchPublicListView(_PublicReadMixin, ListAPIView):
    queryset = Match.objects.select_related(
        "competition", "club_domicile", "club_exterieur"
    ).prefetch_related("buteurs__joueur", "buteurs__joueur__poste")
    serializer_class = MatchPublicSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MatchFilter
    ordering_fields = ["date_heure"]
    ordering = ["date_heure"]


class MatchPublicDetailView(_PublicReadMixin, RetrieveAPIView):
    queryset = Match.objects.select_related(
        "competition", "club_domicile", "club_exterieur"
    ).prefetch_related("buteurs__joueur", "buteurs__joueur__poste")
    serializer_class = MatchPublicSerializer


class StatistiquesPublicView(_PublicReadMixin, ListAPIView):
    serializer_class = StatistiqueJoueurPublicSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["buts", "passes_decisives", "clean_sheets", "matchs_joues"]
    ordering = ["-buts", "-passes_decisives", "-clean_sheets"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return StatistiqueJoueur.objects.filter(
            competition_id=self.kwargs["competition_id"]
        ).select_related("joueur", "joueur__poste", "competition")


@extend_schema(responses={(200, "application/pdf"): OpenApiTypes.BINARY})
class CalendrierPublicDownloadView(_PublicReadMixin, APIView):
    """Téléchargement public du calendrier PDF, filtrable par compétition."""

    def get(self, request):  # type: ignore[no-untyped-def]
        competition_id = request.query_params.get("competition")
        try:
            competition_id_int = int(competition_id) if competition_id else None
        except (TypeError, ValueError):
            raise Http404("Compétition invalide.")
        pdf = build_calendrier_pdf(competition_id_int)
        filename = f"calendrier-{timezone.now():%Y%m%d}.pdf"
        return FileResponse(pdf, as_attachment=True, filename=filename)
