"""Administration Django des ressources sportives."""

from django.contrib import admin

from apps.competitions.models import (
    ButeurMatch,
    ClassementLigne,
    Club,
    Competition,
    Match,
    ParcoursClub,
    ParticipationMatch,
    StatistiqueJoueur,
)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("nom", "sport", "pays", "type", "saison", "actif", "derniere_synchronisation")
    list_filter = ("sport", "pays", "type", "actif", "saison")
    search_fields = ("nom", "saison")
    filter_horizontal = ("clubs",)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("nom", "pays", "sport", "ville", "stade", "fondation")
    list_filter = ("pays", "sport")
    search_fields = ("nom", "ville", "stade")


@admin.register(ParcoursClub)
class ParcoursClubAdmin(admin.ModelAdmin):
    list_display = ("club", "competition", "saison", "position_finale", "ordre")
    list_filter = ("saison",)
    search_fields = ("club__nom", "competition", "position_finale")


class ButeurMatchInline(admin.TabularInline):
    model = ButeurMatch
    extra = 0
    autocomplete_fields = ("joueur", "passeur")


class ParticipationMatchInline(admin.TabularInline):
    model = ParticipationMatch
    extra = 0
    autocomplete_fields = ("joueur",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "date_heure",
        "competition",
        "club_domicile",
        "club_exterieur",
        "adversaire_texte",
        "score_domicile",
        "score_exterieur",
        "statut",
    )
    list_filter = ("competition", "statut")
    search_fields = ("club_domicile__nom", "club_exterieur__nom", "adversaire_texte")
    date_hierarchy = "date_heure"
    autocomplete_fields = ("competition", "club_domicile", "club_exterieur")
    inlines = (ButeurMatchInline, ParticipationMatchInline)


@admin.register(ClassementLigne)
class ClassementLigneAdmin(admin.ModelAdmin):
    list_display = ("competition", "club", "matchs_joues", "points", "buts_pour", "buts_contre")
    list_filter = ("competition",)
    readonly_fields = (
        "competition",
        "club",
        "matchs_joues",
        "victoires",
        "nuls",
        "defaites",
        "buts_pour",
        "buts_contre",
        "points",
    )

    def has_add_permission(self, request):  # type: ignore[no-untyped-def]
        return False

    def has_change_permission(self, request, obj=None):  # type: ignore[no-untyped-def]
        return request.method in ("GET", "HEAD")


@admin.register(StatistiqueJoueur)
class StatistiqueJoueurAdmin(admin.ModelAdmin):
    list_display = ("joueur", "competition", "buts", "passes_decisives", "clean_sheets")
    list_filter = ("competition",)
    search_fields = ("joueur__nom", "joueur__prenom")
    readonly_fields = (
        "joueur",
        "competition",
        "matchs_joues",
        "buts",
        "passes_decisives",
        "cartons_jaunes",
        "cartons_rouges",
        "clean_sheets",
    )

    def has_add_permission(self, request):  # type: ignore[no-untyped-def]
        return False

    def has_change_permission(self, request, obj=None):  # type: ignore[no-untyped-def]
        return request.method in ("GET", "HEAD")
