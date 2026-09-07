"""Filtres de la galerie."""

import django_filters

from apps.galerie.models import AlbumGalerie, ImageGalerie


class AlbumGalerieFilter(django_filters.FilterSet):
    class Meta:
        model = AlbumGalerie
        fields = ["match_lie"]


class ImageGalerieFilter(django_filters.FilterSet):
    class Meta:
        model = ImageGalerie
        fields = ["album", "album__match_lie"]
