"""API rédactionnelle et publique des joueurs expatriés."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.core.permissions import IsEditeurOuPlus, IsRedacteurOuPlus
from apps.expatries.filters import ClubEtrangerFilter, JoueurExpatrieFilter, TransfertFilter
from apps.expatries.models import ClubEtranger, JoueurExpatrie, Transfert
from apps.expatries.serializers import (
    ClubEtrangerPublicSerializer,
    ClubEtrangerSerializer,
    JoueurExpatriePublicSerializer,
    JoueurExpatrieSerializer,
    TransfertPublicSerializer,
    TransfertSerializer,
)
from apps.vitrine.throttles import PublicReadThrottle


class ReadRedacteurWriteEditeurMixin:
    """Le catalogue est lisible par la rédaction, modifiable par les éditeurs."""

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {"list", "retrieve"}:
            return [IsRedacteurOuPlus()]
        return [IsEditeurOuPlus()]


class ClubEtrangerViewSet(ReadRedacteurWriteEditeurMixin, viewsets.ModelViewSet):
    queryset = ClubEtranger.objects.all()
    serializer_class = ClubEtrangerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClubEtrangerFilter
    search_fields = ["nom", "pays", "ligue"]
    ordering_fields = ["nom", "pays", "ligue"]


class JoueurExpatrieViewSet(ReadRedacteurWriteEditeurMixin, viewsets.ModelViewSet):
    queryset = JoueurExpatrie.objects.select_related(
        "joueur", "joueur__poste", "club_etranger"
    )
    serializer_class = JoueurExpatrieSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JoueurExpatrieFilter
    search_fields = ["joueur__nom", "joueur__prenom", "club_etranger__nom"]
    ordering_fields = ["date_arrivee", "created_at", "joueur__nom"]


class TransfertViewSet(ReadRedacteurWriteEditeurMixin, viewsets.ModelViewSet):
    queryset = Transfert.objects.select_related("joueur", "joueur__poste")
    serializer_class = TransfertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransfertFilter
    search_fields = ["joueur__nom", "joueur__prenom", "club_origine", "club_destination"]
    ordering_fields = ["date_transfert", "created_at"]
    ordering = ["-date_transfert"]


class _PublicReadMixin:
    permission_classes = [AllowAny]
    throttle_classes = [PublicReadThrottle]
    throttle_scope = "public-read"


class ClubEtrangerPublicListView(_PublicReadMixin, ListAPIView):
    queryset = ClubEtranger.objects.all()
    serializer_class = ClubEtrangerPublicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClubEtrangerFilter
    search_fields = ["nom", "pays", "ligue"]
    ordering_fields = ["nom", "pays"]


class JoueurExpatriePublicListView(_PublicReadMixin, ListAPIView):
    queryset = JoueurExpatrie.objects.select_related(
        "joueur", "joueur__poste", "club_etranger"
    )
    serializer_class = JoueurExpatriePublicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JoueurExpatrieFilter
    search_fields = ["joueur__nom", "joueur__prenom", "club_etranger__nom"]
    ordering_fields = ["date_arrivee", "joueur__nom"]
    ordering = ["-en_vedette", "joueur__nom"]


class TransfertPublicListView(_PublicReadMixin, ListAPIView):
    queryset = Transfert.objects.select_related("joueur", "joueur__poste")
    serializer_class = TransfertPublicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransfertFilter
    search_fields = ["joueur__nom", "joueur__prenom", "club_origine", "club_destination"]
    ordering_fields = ["date_transfert"]
    ordering = ["-date_transfert"]
