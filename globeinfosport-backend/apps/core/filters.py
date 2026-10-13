"""Geographic filters shared by sports directories."""
import django_filters


class GeographicFilter(django_filters.FilterSet):
    region = django_filters.CharFilter(field_name="pays__region")
    zone = django_filters.CharFilter(method="filter_zone")

    def filter_zone(self, queryset, name, value):
        if value == "haiti":
            return queryset.filter(pays__code="HT")
        if value == "international":
            return queryset.filter(pays__isnull=False).exclude(pays__code="HT")
        return queryset
