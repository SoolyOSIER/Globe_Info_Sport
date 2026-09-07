"""Django administration for public-site content and inboxes."""

from django.contrib import admin

from .models import AbonneNewsletter, FAQ, MessageContact, PageContenu, Partenaire


@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ("nom", "email", "sujet", "traite", "created_at")
    list_filter = ("traite",)
    search_fields = ("nom", "email", "sujet", "message")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AbonneNewsletter)
class AbonneNewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "actif", "created_at")
    list_filter = ("actif",)
    search_fields = ("email",)
    readonly_fields = ("token_desabonnement", "created_at", "updated_at")


@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ("nom", "ordre", "actif")
    list_editable = ("ordre", "actif")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "ordre")
    list_editable = ("ordre",)


@admin.register(PageContenu)
class PageContenuAdmin(admin.ModelAdmin):
    list_display = ("cle", "titre", "actif", "updated_at")
    list_filter = ("actif",)
    search_fields = ("cle", "titre", "contenu")
