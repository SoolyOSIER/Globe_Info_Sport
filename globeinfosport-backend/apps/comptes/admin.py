from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm

from .forms import UtilisateurChangeForm, UtilisateurCreationForm
from .models import RoleRedaction, Utilisateur


@admin.register(RoleRedaction)
class RoleRedactionAdmin(admin.ModelAdmin):
    list_display = ("nomRole",)
    search_fields = ("nomRole",)


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    """Administration adaptée au USERNAME_FIELD ``identifiant``."""

    add_form = UtilisateurCreationForm
    form = UtilisateurChangeForm
    change_password_form = AdminPasswordChangeForm
    model = Utilisateur
    list_display = (
        "identifiant",
        "nom",
        "prenom",
        "role_redaction",
        "is_active",
        "is_staff",
        "dernier_acces",
    )
    list_filter = ("role_redaction", "is_active", "is_staff", "is_superuser")
    search_fields = ("identifiant", "nom", "prenom", "email")
    ordering = ("identifiant",)
    readonly_fields = ("date_creation_compte", "dernier_acces", "last_login")
    fieldsets = (
        (None, {"fields": ("identifiant", "password")}),
        (
            "Informations personnelles",
            {"fields": ("nom", "prenom", "email", "photo", "bio")},
        ),
        ("Rédaction", {"fields": ("role_redaction",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Dates",
            {"fields": ("last_login", "date_creation_compte", "dernier_acces")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "identifiant",
                    "nom",
                    "prenom",
                    "email",
                    "role_redaction",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )
