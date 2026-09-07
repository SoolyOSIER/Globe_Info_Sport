"""Back-up d'administration des données SPI."""

from django.contrib import admin

from apps.expatries.models import ClubEtranger, JoueurExpatrie, Transfert


@admin.register(ClubEtranger)
class ClubEtrangerAdmin(admin.ModelAdmin):
    list_display = ("nom", "pays", "ligue")
    search_fields = ("nom", "pays", "ligue")
    list_filter = ("pays",)


@admin.register(JoueurExpatrie)
class JoueurExpatrieAdmin(admin.ModelAdmin):
    list_display = ("joueur", "club_etranger", "statut", "en_vedette", "date_arrivee")
    list_filter = ("statut", "en_vedette", "club_etranger__pays")
    search_fields = ("joueur__nom", "joueur__prenom", "club_etranger__nom")
    autocomplete_fields = ("joueur", "club_etranger")


@admin.register(Transfert)
class TransfertAdmin(admin.ModelAdmin):
    list_display = (
        "joueur",
        "club_origine",
        "club_destination",
        "date_transfert",
        "type_transfert",
    )
    list_filter = ("type_transfert", "date_transfert")
    search_fields = ("joueur__nom", "joueur__prenom", "club_origine", "club_destination")
    autocomplete_fields = ("joueur",)
    date_hierarchy = "date_transfert"
