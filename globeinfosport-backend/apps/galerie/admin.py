"""Administration de secours des albums et images."""

from django.contrib import admin

from apps.galerie.models import AlbumGalerie, ImageGalerie


class ImageGalerieInline(admin.TabularInline):
    model = ImageGalerie
    extra = 0
    fields = ("image", "legende", "ordre")


@admin.register(AlbumGalerie)
class AlbumGalerieAdmin(admin.ModelAdmin):
    list_display = ("titre", "match_lie", "created_at")
    search_fields = ("titre", "description")
    autocomplete_fields = ("match_lie",)
    inlines = (ImageGalerieInline,)


@admin.register(ImageGalerie)
class ImageGalerieAdmin(admin.ModelAdmin):
    list_display = ("album", "legende", "ordre", "created_at")
    list_filter = ("album",)
    search_fields = ("legende", "album__titre")
    autocomplete_fields = ("album",)
