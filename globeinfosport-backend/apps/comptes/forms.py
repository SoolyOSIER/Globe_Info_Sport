"""Formulaires Django Admin du modèle utilisateur personnalisé."""

from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Utilisateur


class UtilisateurCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ("identifiant", "nom", "prenom", "email", "role_redaction")


class UtilisateurChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Utilisateur
        fields = "__all__"
