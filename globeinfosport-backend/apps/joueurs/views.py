from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.core.permissions import IsEditeurOuPlus, IsRedacteurOuPlus

from .filters import JoueurFilter
from .models import Joueur, Legende, Poste
from .serializers import (
    JoueurCreateSerializer,
    JoueurDetailSerializer,
    JoueurListSerializer,
    JoueurPublicSerializer,
    LegendePublicSerializer,
    LegendeSerializer,
    PosteSerializer,
)


class JoueurViewSet(viewsets.ModelViewSet):
    """Gestion de la base joueurs de la sélection nationale."""

    queryset = Joueur.objects.select_related("poste").all()
    permission_classes = [IsRedacteurOuPlus]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JoueurFilter
    search_fields = ["nom", "prenom", "club_actuel"]
    ordering_fields = ["nom", "prenom", "nb_selections", "nb_buts_selection"]
    ordering = ["nom", "prenom"]

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "list":
            return JoueurListSerializer
        if self.action in {"create", "update", "partial_update"}:
            return JoueurCreateSerializer
        return JoueurDetailSerializer


class PosteListView(ListAPIView):
    """Référentiel en lecture seule pour les formulaires de joueurs."""

    queryset = Poste.objects.all()
    serializer_class = PosteSerializer
    permission_classes = [IsRedacteurOuPlus]


class LegendeViewSet(viewsets.ModelViewSet):
    """Gestion réservée au contenu historique validé par l'équipe éditoriale."""

    queryset = Legende.objects.all()
    serializer_class = LegendeSerializer
    permission_classes = [IsEditeurOuPlus]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nom", "poste", "biographie", "exploits"]
    ordering_fields = ["ordre_affichage", "nom", "created_at"]
    ordering = ["ordre_affichage", "nom"]


class JoueurPublicListView(ListAPIView):
    """Liste publique de joueurs, pour l'accueil et la page championnat."""

    queryset = Joueur.objects.select_related("poste").all()
    serializer_class = JoueurPublicSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JoueurFilter
    search_fields = ["nom", "prenom", "club_actuel"]
    ordering_fields = ["nom", "prenom", "nb_selections", "nb_buts_selection"]
    ordering = ["nom", "prenom"]


class LegendePublicListView(ListAPIView):
    """Liste publique ordonnée des légendes du football haïtien."""

    queryset = Legende.objects.all()
    serializer_class = LegendePublicSerializer
    permission_classes = [AllowAny]
    throttle_scope = "public-read"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nom", "poste", "biographie", "exploits"]
    ordering_fields = ["ordre_affichage", "nom"]
    ordering = ["ordre_affichage", "nom"]
