"""Serializers de la galerie rédactionnelle et publique."""

from rest_framework import serializers

from apps.galerie.models import AlbumGalerie, ImageGalerie


class ImageGalerieSerializer(serializers.ModelSerializer):
    album_titre = serializers.CharField(source="album.titre", read_only=True)

    class Meta:
        model = ImageGalerie
        fields = [
            "id",
            "album",
            "album_titre",
            "image",
            "legende",
            "ordre",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ImageGaleriePublicSerializer(ImageGalerieSerializer):
    """Image accompagnée des seules métadonnées nécessaires à la vitrine."""


class AlbumGalerieSerializer(serializers.ModelSerializer):
    images = ImageGalerieSerializer(many=True, read_only=True)
    nombre_images = serializers.IntegerField(source="images.count", read_only=True)
    match_lie_affichage = serializers.SerializerMethodField()

    class Meta:
        model = AlbumGalerie
        fields = [
            "id",
            "titre",
            "match_lie",
            "match_lie_affichage",
            "description",
            "nombre_images",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "nombre_images", "images"]

    def get_match_lie_affichage(self, obj: AlbumGalerie) -> str | None:
        return str(obj.match_lie) if obj.match_lie else None


class AlbumGaleriePublicSerializer(AlbumGalerieSerializer):
    """Alias explicite de la ressource d'album publique."""
