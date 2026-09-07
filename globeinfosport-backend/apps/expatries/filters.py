"""Filtres de recherche pour la rubrique expatriés."""

import django_filters

from apps.expatries.models import ClubEtranger, JoueurExpatrie, Transfert


class ClubEtrangerFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(field_name="nom", lookup_expr="icontains")
    pays = django_filters.CharFilter(field_name="pays", lookup_expr="icontains")
    ligue = django_filters.CharFilter(field_name="ligue", lookup_expr="icontains")

    class Meta:
        model = ClubEtranger
        fields = ["nom", "pays", "ligue"]


class JoueurExpatrieFilter(django_filters.FilterSet):
    pays = django_filters.CharFilter(field_name="club_etranger__pays", lookup_expr="iexact")

    class Meta:
        model = JoueurExpatrie
        fields = ["statut", "club_etranger", "en_vedette", "pays"]


class TransfertFilter(django_filters.FilterSet):
    date_debut = django_filters.DateFilter(field_name="date_transfert", lookup_expr="gte")
    date_fin = django_filters.DateFilter(field_name="date_transfert", lookup_expr="lte")

    class Meta:
        model = Transfert
        fields = ["joueur", "type_transfert"]
