import django_filters

from .models import Article


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

    class Meta:
        model = Article
        fields = ["categorie", "tags", "statut", "a_la_une"]
