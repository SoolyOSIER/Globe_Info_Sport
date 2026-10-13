import django_filters
from apps.core.filters import GeographicFilter

from .models import Joueur


class JoueurFilter(GeographicFilter):
    """Filtres partagés entre la recherche interne et la vitrine."""

    poste_nom = django_filters.CharFilter(
        field_name="poste__nom",
        lookup_expr="iexact",
    )

    class Meta:
        model = Joueur
        fields = ["poste", "selection_nationale", "emblematique", "sport", "pays"]
