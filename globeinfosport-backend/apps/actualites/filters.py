import django_filters

from apps.core.filters import GeographicFilter
from .models import Article, Selection, Pays


class ArticleFilter(django_filters.FilterSet):
    """Filtres complémentaires pour les listes éditoriales et publiques."""

    date_debut = django_filters.DateFilter(
        field_name="date_publication",
        lookup_expr="date__gte",
    )
    date_fin = django_filters.DateFilter(
        field_name="date_publication",
        lookup_expr="date__lte",
    )
    categorie_slug = django_filters.CharFilter(
        field_name="categorie__slug",
        lookup_expr="iexact",
    )

    pays_code = django_filters.CharFilter(field_name="pays__code", lookup_expr="iexact")
    region = django_filters.CharFilter(field_name="pays__region")
    sport_slug = django_filters.CharFilter(field_name="sport__slug")
    tag = django_filters.CharFilter(field_name="tags__slug")
    zone = django_filters.CharFilter(method="filter_zone")

    def filter_zone(self, queryset, name, value):
        if value == "haiti":
            return queryset.filter(pays__code="HT").distinct()
        if value == "international":
            return queryset.filter(pays__in=Pays.objects.exclude(code="HT")).distinct()
        return queryset

    class Meta:
        model = Article
        fields = ["categorie", "tags", "statut", "a_la_une", "sport", "pays", "clubs", "competitions", "selections", "athletes", "breaking", "recommande"]


class SelectionFilter(GeographicFilter):
    class Meta:
        model = Selection
        fields = ["pays", "sport", "competitions"]
