from django.contrib import admin

from .models import Article, Categorie, ChiffreCle, Citation, Tag, Video


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug")
    prepopulated_fields = {"slug": ("nom",)}
    search_fields = ("nom",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug")
    prepopulated_fields = {"slug": ("nom",)}
    search_fields = ("nom",)


class VideoInline(admin.TabularInline):
    model = Video
    extra = 0


class CitationInline(admin.TabularInline):
    model = Citation
    extra = 0


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "titre",
        "categorie",
        "auteur",
        "statut",
        "a_la_une",
        "date_publication",
        "compteur_vues",
    )
    list_filter = ("statut", "a_la_une", "categorie", "tags")
    search_fields = ("titre", "chapo", "contenu", "source")
    prepopulated_fields = {"slug": ("titre",)}
    autocomplete_fields = ("auteur",)
    filter_horizontal = ("tags",)
    readonly_fields = ("compteur_vues", "created_at", "updated_at")
    date_hierarchy = "date_publication"
    inlines = (VideoInline, CitationInline)

    def save_model(self, request, obj, form, change) -> None:  # type: ignore[no-untyped-def]
        if not change and not obj.auteur_id:
            obj.auteur = request.user
        super().save_model(request, obj, form, change)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("titre", "article_lie", "a_la_une", "ordre", "created_at")
    list_filter = ("a_la_une",)
    search_fields = ("titre",)


@admin.register(Citation)
class CitationAdmin(admin.ModelAdmin):
    list_display = ("auteur_nom", "auteur_fonction", "article_lie", "ordre")
    search_fields = ("auteur_nom", "auteur_fonction", "texte")


@admin.register(ChiffreCle)
class ChiffreCleAdmin(admin.ModelAdmin):
    list_display = ("libelle", "valeur", "calcule_auto", "code_calcul", "ordre")
    list_editable = ("ordre",)
    list_filter = ("calcule_auto",)
    search_fields = ("libelle", "code_calcul")
