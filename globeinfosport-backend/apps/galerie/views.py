"""Vues privées et publiques de la galerie photos."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.core.permissions import IsRedacteurOuPlus
from apps.galerie.filters import AlbumGalerieFilter, ImageGalerieFilter
from apps.galerie.models import AlbumGalerie, ImageGalerie
from apps.galerie.serializers import (
    AlbumGaleriePublicSerializer,
    AlbumGalerieSerializer,
    ImageGaleriePublicSerializer,
    ImageGalerieSerializer,
)
from apps.vitrine.throttles import PublicReadThrottle


class AlbumGalerieViewSet(viewsets.ModelViewSet):
    queryset = AlbumGalerie.objects.select_related(
        "match_lie", "match_lie__club_domicile", "match_lie__club_exterieur"
    ).prefetch_related("images")
    serializer_class = AlbumGalerieSerializer
    permission_classes = [IsRedacteurOuPlus]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AlbumGalerieFilter
    search_fields = ["titre", "description"]
    ordering_fields = ["titre", "created_at"]


class ImageGalerieViewSet(viewsets.ModelViewSet):
    queryset = ImageGalerie.objects.select_related("album", "album__match_lie")
    serializer_class = ImageGalerieSerializer
    permission_classes = [IsRedacteurOuPlus]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ImageGalerieFilter
    search_fields = ["legende", "album__titre"]
    ordering_fields = ["ordre", "created_at"]


class _PublicReadMixin:
    permission_classes = [AllowAny]
    throttle_classes = [PublicReadThrottle]
    throttle_scope = "public-read"


class ImageGaleriePublicListView(_PublicReadMixin, ListAPIView):
    """Retourne les photos, chaque photo comportant la référence à son album."""

    queryset = ImageGalerie.objects.select_related("album", "album__match_lie")
    serializer_class = ImageGaleriePublicSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ImageGalerieFilter
    ordering_fields = ["ordre", "created_at"]
    ordering = ["ordre", "-created_at"]


class AlbumGaleriePublicListView(_PublicReadMixin, ListAPIView):
    queryset = AlbumGalerie.objects.select_related("match_lie").prefetch_related("images")
    serializer_class = AlbumGaleriePublicSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AlbumGalerieFilter
    ordering_fields = ["created_at", "titre"]
