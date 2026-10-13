from __future__ import annotations

from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import RoleRedaction, Utilisateur


class RoleRedactionSerializer(serializers.ModelSerializer):
    """Représentation stable d'un rôle éditorial."""

    libelle = serializers.CharField(source="get_nomRole_display", read_only=True)

    class Meta:
        model = RoleRedaction
        fields = ["id", "nomRole", "libelle"]
        read_only_fields = ["id", "libelle"]


class UtilisateurSerializer(serializers.ModelSerializer):
    """Profil exposé au back-office et au flux d'authentification."""

    role_redaction = RoleRedactionSerializer(read_only=True)
    nom_complet = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "identifiant",
            "nom",
            "prenom",
            "nom_complet",
            "email",
            "photo",
            "bio",
            "role_redaction",
            "is_active",
            "is_superuser",
            "date_creation_compte",
            "dernier_acces",
        ]
        read_only_fields = ["id", "is_superuser", "date_creation_compte", "dernier_acces"]


class UtilisateurCreateSerializer(serializers.ModelSerializer):
    """Création d'un compte avec hachage du mot de passe côté serveur."""

    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "identifiant",
            "nom",
            "prenom",
            "email",
            "photo",
            "bio",
            "role_redaction",
            "is_active",
            "password",
        ]
        read_only_fields = ["id"]

    def validate_password(self, value: str) -> str:
        candidate = Utilisateur(
            identifiant=self.initial_data.get("identifiant", ""),
            nom=self.initial_data.get("nom", ""),
            prenom=self.initial_data.get("prenom", ""),
            email=self.initial_data.get("email", ""),
        )
        password_validation.validate_password(value, candidate)
        return value

    def create(self, validated_data: dict) -> Utilisateur:
        password = validated_data.pop("password")
        return Utilisateur.objects.create_user(password=password, **validated_data)


class UtilisateurUpdateSerializer(serializers.ModelSerializer):
    """Mise à jour d'un compte, avec changement de mot de passe facultatif."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        trim_whitespace=False,
    )

    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "identifiant",
            "nom",
            "prenom",
            "email",
            "photo",
            "bio",
            "role_redaction",
            "is_active",
            "password",
        ]
        read_only_fields = ["id"]

    def validate_password(self, value: str) -> str:
        password_validation.validate_password(value, self.instance)
        return value

    def update(self, instance: Utilisateur, validated_data: dict) -> Utilisateur:
        password = validated_data.pop("password", None)
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        if password:
            instance.set_password(password)
        instance.full_clean()
        instance.save()
        return instance
