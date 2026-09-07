from __future__ import annotations

from rest_framework import serializers

from .models import Joueur, Legende, Poste


class PosteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poste
        fields = ["id", "nom"]
        read_only_fields = ["id"]


class JoueurListSerializer(serializers.ModelSerializer):
    """Projection compacte des joueurs pour les listes et tableaux."""

    poste = PosteSerializer(read_only=True)
    nom_complet = serializers.CharField(read_only=True)

    class Meta:
        model = Joueur
        fields = [
            "id",
            "nom",
            "prenom",
            "nom_complet",
            "photo",
            "poste",
            "club_actuel",
            "numero_maillot",
            "selection_nationale",
            "nb_selections",
            "nb_buts_selection",
            "emblematique",
        ]


class JoueurDetailSerializer(JoueurListSerializer):
    """Fiche complète utilisée dans le formulaire de gestion des joueurs."""

    class Meta(JoueurListSerializer.Meta):
        fields = [
            *JoueurListSerializer.Meta.fields,
            "date_naissance",
            "taille_cm",
            "pied_fort",
            "biographie",
            "created_at",
            "updated_at",
        ]


class JoueurCreateSerializer(serializers.ModelSerializer):
    """Écriture de la fiche joueur depuis le back-office."""

    class Meta:
        model = Joueur
        fields = [
            "id",
            "nom",
            "prenom",
            "photo",
            "date_naissance",
            "poste",
            "club_actuel",
            "numero_maillot",
            "taille_cm",
            "pied_fort",
            "biographie",
            "selection_nationale",
            "nb_selections",
            "nb_buts_selection",
            "emblematique",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs: dict) -> dict:
        candidate = self.instance or Joueur()
        for field, value in attrs.items():
            setattr(candidate, field, value)
        candidate.full_clean()
        return attrs


class LegendeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legende
        fields = [
            "id",
            "nom",
            "photo",
            "periode_active",
            "poste",
            "biographie",
            "exploits",
            "ordre_affichage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class JoueurPublicSerializer(serializers.ModelSerializer):
    """Fiche joueur consommée par le site vitrine, sans métadonnées internes."""

    poste = PosteSerializer(read_only=True)
    nom_complet = serializers.CharField(read_only=True)

    class Meta:
        model = Joueur
        fields = [
            "id",
            "nom",
            "prenom",
            "nom_complet",
            "photo",
            "date_naissance",
            "poste",
            "club_actuel",
            "numero_maillot",
            "taille_cm",
            "pied_fort",
            "biographie",
            "selection_nationale",
            "nb_selections",
            "nb_buts_selection",
            "emblematique",
        ]


class LegendePublicSerializer(serializers.ModelSerializer):
    """Présentation publique des légendes historiques."""

    class Meta:
        model = Legende
        fields = [
            "id",
            "nom",
            "photo",
            "periode_active",
            "poste",
            "biographie",
            "exploits",
            "ordre_affichage",
        ]
