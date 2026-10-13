"""Filtres déclaratifs des ressources de compétitions."""

import django_filters
from apps.core.filters import GeographicFilter

from apps.competitions.models import Club, Competition, Match, StatistiqueJoueur


class CompetitionFilter(GeographicFilter):
    class Meta:
        model = Competition
        fields = {
            "type": ["exact"],
            "saison": ["exact"],
            "actif": ["exact"],
            "sport": ["exact"],
            "pays": ["exact"],
        }


class ClubFilter(GeographicFilter):
    nom = django_filters.CharFilter(field_name="nom", lookup_expr="icontains")
    ville = django_filters.CharFilter(field_name="ville", lookup_expr="icontains")

    class Meta:
        model = Club
        fields = ["nom", "ville", "sport", "pays"]


class MatchFilter(django_filters.FilterSet):
    date_debut = django_filters.IsoDateTimeFilter(
        field_name="date_heure", lookup_expr="gte"
    )
    date_fin = django_filters.IsoDateTimeFilter(field_name="date_heure", lookup_expr="lte")
    mois = django_filters.NumberFilter(field_name="date_heure", lookup_expr="month")
    annee = django_filters.NumberFilter(field_name="date_heure", lookup_expr="year")
    # Alias documentés dans le contrat public de l'API.
    date_heure__month = django_filters.NumberFilter(
        field_name="date_heure", lookup_expr="month"
    )
    date_heure__year = django_filters.NumberFilter(
        field_name="date_heure", lookup_expr="year"
    )

    class Meta:
        model = Match
        fields = ["competition", "club_domicile", "club_exterieur", "statut"]


class StatistiqueJoueurFilter(django_filters.FilterSet):
    class Meta:
        model = StatistiqueJoueur
        fields = ["competition", "joueur"]
