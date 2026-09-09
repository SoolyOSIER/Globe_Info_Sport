"""Serializers des formulaires publics et des référentiels de vitrine."""

from __future__ import annotations

from typing import Any

import requests
from django.conf import settings
from rest_framework import serializers

from apps.vitrine.models import (
    AbonneNewsletter,
    FAQ,
    MessageContact,
    PageContenu,
    Partenaire,
)


def verifier_recaptcha(token: str) -> bool:
    """Vérifie un jeton reCAPTCHA v3 et son score côté serveur.

    En développement sans clé, la vérification est volontairement permissive
    afin que les tests locaux ne dépendent pas de Google. Hors DEBUG, une clé
    manquante est toujours un refus sécurisé.
    """

    secret = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
    if not secret:
        return bool(getattr(settings, "DEBUG", False))
    if not token:
        return False
    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": token},
            timeout=5,
        )
        payload = response.json()
    except (requests.RequestException, ValueError):
        return False
    return bool(payload.get("success")) and float(payload.get("score", 0)) >= float(
        getattr(settings, "RECAPTCHA_MIN_SCORE", 0.5)
    )


class MessageContactCreateSerializer(serializers.ModelSerializer):
    honeypot = serializers.CharField(required=False, allow_blank=True, write_only=True)
    recaptcha_token = serializers.CharField(write_only=True)

    class Meta:
        model = MessageContact
        fields = ["nom", "email", "sujet", "message", "honeypot", "recaptcha_token"]

    def validate_honeypot(self, value: str) -> str:
        if value.strip():
            raise serializers.ValidationError("Requête invalide.")
        return value

    def validate_recaptcha_token(self, value: str) -> str:
        if not verifier_recaptcha(value):
            raise serializers.ValidationError("Vérification anti-spam échouée.")
        return value

    def validate_message(self, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Votre message doit contenir au moins 10 caractères.")
        return value

    def create(self, validated_data: dict[str, Any]) -> MessageContact:
        validated_data.pop("honeypot", None)
        validated_data.pop("recaptcha_token", None)
        return super().create(validated_data)


class AbonneNewsletterCreateSerializer(serializers.ModelSerializer):
    honeypot = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = AbonneNewsletter
        fields = ["email", "honeypot"]

    def validate_honeypot(self, value: str) -> str:
        if value.strip():
            raise serializers.ValidationError("Requête invalide.")
        return value

    def validate_email(self, value: str) -> str:
        return value.lower().strip()

    def create(self, validated_data: dict[str, Any]) -> AbonneNewsletter:
        validated_data.pop("honeypot", None)
        email = validated_data["email"]
        abonne, created = AbonneNewsletter.objects.get_or_create(email=email)
        if not created and not abonne.actif:
            abonne.actif = True
            abonne.save(update_fields=["actif", "updated_at"])
        # Un abonné actif reçoit une réponse idempotente sans second courriel.
        self._was_created = created
        return abonne


class NewsletterUnsubscribeSerializer(serializers.Serializer):
    """Schéma explicite de la route de désabonnement par jeton d'URL."""

    # Le jeton est un paramètre de chemin, il n'y a donc pas de corps à valider.
    pass


class MessageContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageContact
        fields = ["id", "nom", "email", "sujet", "message", "traite", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AbonneNewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbonneNewsletter
        fields = ["id", "email", "actif", "token_desabonnement", "created_at", "updated_at"]
        read_only_fields = ["id", "token_desabonnement", "created_at", "updated_at"]


class PartenaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partenaire
        fields = ["id", "nom", "logo", "url", "ordre", "actif"]


class PartenairePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partenaire
        fields = ["id", "nom", "logo", "url"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "reponse", "ordre"]


class FAQPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "reponse"]


class PageContenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageContenu
        fields = ["id", "cle", "titre", "contenu", "image", "actif", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PageContenuPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageContenu
        fields = ["cle", "titre", "contenu", "image"]
