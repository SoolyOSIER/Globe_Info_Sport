from django.contrib import admin

from .models import Joueur, Legende, Poste


@admin.register(Poste)
class PosteAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(Joueur)
class JoueurAdmin(admin.ModelAdmin):
    list_display = (
        "nom_complet",
        "poste",
        "sport",
        "pays",
        "club_actuel",
        "selection_nationale",
        "emblematique",
        "nb_selections",
        "nb_buts_selection",
    )
    list_filter = ("sport", "pays", "poste", "selection_nationale", "emblematique", "pied_fort")
    search_fields = ("nom", "prenom", "club_actuel")
    list_select_related = ("poste", "sport", "pays")
    ordering = ("nom", "prenom")


@admin.register(Legende)
class LegendeAdmin(admin.ModelAdmin):
    list_display = ("nom", "poste", "periode_active", "ordre_affichage")
    list_editable = ("ordre_affichage",)
    search_fields = ("nom", "poste", "biographie", "exploits")
    ordering = ("ordre_affichage", "nom")
