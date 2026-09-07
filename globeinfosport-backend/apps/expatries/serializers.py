"""Serializers de gestion et de consultation des expatriés."""

from __future__ import annotations

from rest_framework import serializers

from apps.expatries.models import ClubEtranger, JoueurExpatrie, Transfert


class ClubEtrangerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubEtranger
        fields = ["id", "nom", "pays", "ligue", "logo"]


class ClubEtrangerPublicSerializer(ClubEtrangerSerializer):
    """Alias public, sans champs d'administration."""


class JoueurExpatrieSerializer(serializers.ModelSerializer):
    joueur_nom = serializers.SerializerMethodField()
    joueur_photo = serializers.SerializerMethodField()
    joueur_poste = serializers.SerializerMethodField()
    club_etranger_detail = ClubEtrangerSerializer(source="club_etranger", read_only=True)

    class Meta:
        model = JoueurExpatrie
        fields = [
            "id",
            "joueur",
            "joueur_nom",
            "joueur_photo",
            "joueur_poste",
            "club_etranger",
            "club_etranger_detail",
            "date_arrivee",
            "statut",
            "en_vedette",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_joueur_nom(self, obj: JoueurExpatrie) -> str:
        return str(obj.joueur)

    def get_joueur_photo(self, obj: JoueurExpatrie) -> str | None:
        photo = getattr(obj.joueur, "photo", None)
        return photo.url if photo else None

    def get_joueur_poste(self, obj: JoueurExpatrie) -> str | None:
        poste = getattr(obj.joueur, "poste", None)
        return getattr(poste, "nom", None)


class JoueurExpatriePublicSerializer(JoueurExpatrieSerializer):
    """Données de fiche nécessaires à la grille publique SPI."""


class TransfertSerializer(serializers.ModelSerializer):
    joueur_nom = serializers.SerializerMethodField()
    joueur_photo = serializers.SerializerMethodField()

    class Meta:
        model = Transfert
        fields = [
            "id",
            "joueur",
            "joueur_nom",
            "joueur_photo",
            "club_origine",
            "club_destination",
            "date_transfert",
            "type_transfert",
            "montant",
            "source",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_joueur_nom(self, obj: Transfert) -> str:
        return str(obj.joueur)

    def get_joueur_photo(self, obj: Transfert) -> str | None:
        photo = getattr(obj.joueur, "photo", None)
        return photo.url if photo else None

    def validate(self, attrs):  # type: ignore[no-untyped-def]
        origin = attrs.get("club_origine", getattr(self.instance, "club_origine", ""))
        destination = attrs.get(
            "club_destination", getattr(self.instance, "club_destination", "")
        )
        if origin and destination and origin.strip().casefold() == destination.strip().casefold():
            raise serializers.ValidationError(
                {"club_destination": "Le club de destination doit être différent du club d'origine."}
            )
        return attrs


class TransfertPublicSerializer(TransfertSerializer):
    """Alias pour le contrat de lecture public."""
