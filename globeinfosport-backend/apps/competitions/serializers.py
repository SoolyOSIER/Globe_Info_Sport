"""Serializers de l'API rédactionnelle et de l'API publique sportive."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from rest_framework import serializers

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
from apps.competitions.services import (
    recalculer_classement,
    recalculer_statistiques_competition,
)


class CompetitionSerializer(serializers.ModelSerializer):
    clubs_detail = serializers.SerializerMethodField()
    pays_detail = serializers.SerializerMethodField()
    sport_detail = serializers.SerializerMethodField()

    def get_clubs_detail(self, obj):
        return ClubResumeSerializer(obj.clubs.all(), many=True, context=self.context).data

    def get_pays_detail(self, obj):
        from apps.actualites.serializers import PaysSerializer

        return PaysSerializer(obj.pays, context=self.context).data if obj.pays else None

    def get_sport_detail(self, obj):
        from apps.actualites.serializers import SportSerializer

        return SportSerializer(obj.sport, context=self.context).data if obj.sport else None

    class Meta:
        model = Competition
        fields = [
            "id", "nom", "type", "saison", "actif", "sport", "sport_detail", "pays", "pays_detail", "description", "logo",
            "clubs", "clubs_detail", "source_donnees", "derniere_synchronisation",
        ]
        read_only_fields = ["source_donnees", "derniere_synchronisation"]


class CompetitionPublicSerializer(CompetitionSerializer):
    """Représentation sans aucun champ de gestion interne."""


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = [
            "id",
            "nom",
            "slug",
            "ville", "sport", "pays", "entraineur",
            "logo",
            "stade",
            "fondation",
            "description",
            "histoire",
            "palmares",
            "couleurs",
            "site_web",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ClubResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["id", "nom", "slug", "ville", "logo"]


class ClubPublicSerializer(ClubResumeSerializer):
    """Fiche publique condensée d'un club."""


class ParcoursClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcoursClub
        fields = ["id", "club", "saison", "competition", "position_finale", "bilan", "recit", "ordre"]
        read_only_fields = ["id"]


class ClubPublicDetailSerializer(ClubSerializer):
    parcours = ParcoursClubSerializer(many=True, read_only=True)

    class Meta(ClubSerializer.Meta):
        fields = ClubSerializer.Meta.fields + ["parcours"]


class ClassementLigneSerializer(serializers.ModelSerializer):
    club_detail = ClubResumeSerializer(source="club", read_only=True)
    difference_buts = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClassementLigne
        fields = [
            "id",
            "competition",
            "club",
            "club_detail",
            "matchs_joues",
            "victoires",
            "nuls",
            "defaites",
            "buts_pour",
            "buts_contre",
            "difference_buts",
            "points",
            "updated_at",
        ]
        read_only_fields = fields


class ClassementPublicSerializer(ClassementLigneSerializer):
    """Alias explicite pour l'API vitrine."""


class ButeurMatchSerializer(serializers.ModelSerializer):
    joueur_nom = serializers.SerializerMethodField()
    passeur_nom = serializers.SerializerMethodField()

    class Meta:
        model = ButeurMatch
        fields = ["id", "joueur", "joueur_nom", "passeur", "passeur_nom", "minute", "type_but"]
        read_only_fields = ["id", "joueur_nom", "passeur_nom"]

    def get_joueur_nom(self, obj: ButeurMatch) -> str:
        return str(obj.joueur)

    def get_passeur_nom(self, obj: ButeurMatch) -> str | None:
        return str(obj.passeur) if obj.passeur else None


class ButeurMatchInputSerializer(serializers.ModelSerializer):
    """Événement autorisé lors de la saisie complète d'un résultat."""

    class Meta:
        model = ButeurMatch
        fields = ["joueur", "passeur", "minute", "type_but"]

    def validate_minute(self, value: int) -> int:
        if value > 130:
            raise serializers.ValidationError("La minute doit être comprise entre 0 et 130.")
        return value


class ParticipationMatchInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipationMatch
        fields = ["joueur", "titulaire", "cartons_jaunes", "carton_rouge", "clean_sheet"]


class MatchListSerializer(serializers.ModelSerializer):
    competition_nom = serializers.CharField(source="competition.nom", read_only=True)
    club_domicile_detail = ClubResumeSerializer(source="club_domicile", read_only=True)
    club_exterieur_detail = ClubResumeSerializer(source="club_exterieur", read_only=True)
    adversaire = serializers.CharField(read_only=True)
    score_affichage = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            "id",
            "competition",
            "competition_nom",
            "club_domicile",
            "club_domicile_detail",
            "club_exterieur",
            "club_exterieur_detail",
            "adversaire_texte",
            "adversaire",
            "date_heure",
            "lieu",
            "diffusion_tv",
            "score_domicile",
            "score_exterieur",
            "score_affichage",
            "statut",
        ]

    def get_score_affichage(self, obj: Match) -> str | None:
        if obj.score_domicile is None or obj.score_exterieur is None:
            return None
        return f"{obj.score_domicile} - {obj.score_exterieur}"

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Applique les validations du modèle aussi aux créations partielles."""

        instance = self.instance
        values = {
            field: attrs.get(field, getattr(instance, field, None))
            for field in (
                "club_domicile",
                "club_exterieur",
                "adversaire_texte",
                "score_domicile",
                "score_exterieur",
                "statut",
            )
        }
        domicile = values["club_domicile"]
        exterieur = values["club_exterieur"]
        if domicile and exterieur and domicile.pk == exterieur.pk:
            raise serializers.ValidationError(
                {"club_exterieur": "Le club extérieur doit être différent du club domicile."}
            )
        if not exterieur and not (values["adversaire_texte"] or "").strip():
            raise serializers.ValidationError(
                {"adversaire_texte": "Un adversaire doit être renseigné."}
            )
        home_score, away_score = values["score_domicile"], values["score_exterieur"]
        if (home_score is None) != (away_score is None):
            raise serializers.ValidationError(
                "Les scores domicile et extérieur doivent être fournis ensemble."
            )
        if values["statut"] == Match.Statut.TERMINE and (
            home_score is None or away_score is None
        ):
            raise serializers.ValidationError(
                {"statut": "Un match terminé doit disposer de ses deux scores."}
            )
        return attrs


class MatchDetailSerializer(MatchListSerializer):
    buteurs = ButeurMatchSerializer(many=True, read_only=True)
    participations = ParticipationMatchInputSerializer(many=True, read_only=True)
    resume = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta(MatchListSerializer.Meta):
        fields = MatchListSerializer.Meta.fields + [
            "resume",
            "buteurs",
            "participations",
            "created_at",
            "updated_at",
        ]


class MatchPublicSerializer(MatchDetailSerializer):
    """Données nécessaires au calendrier et au direct de la vitrine."""


class MatchResultatSerializer(serializers.ModelSerializer):
    """Saisie atomique du score final et de la liste complète des buteurs."""

    buteurs = ButeurMatchInputSerializer(many=True, required=False)
    participations = ParticipationMatchInputSerializer(many=True, required=False)

    class Meta:
        model = Match
        fields = ["score_domicile", "score_exterieur", "resume", "buteurs", "participations"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs.get("score_domicile") is None or attrs.get("score_exterieur") is None:
            raise serializers.ValidationError(
                "Les scores domicile et extérieur sont obligatoires pour un résultat final."
            )
        return attrs

    @transaction.atomic
    def update(self, instance: Match, validated_data: dict[str, Any]) -> Match:
        buteurs_data = validated_data.pop("buteurs", None)
        participations_data = validated_data.pop("participations", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.statut = Match.Statut.TERMINE
        instance.full_clean()
        instance.save()

        # L'absence du champ laisse les buteurs existants intacts, ce qui est
        # utile lorsqu'on corrige seulement le score ou le résumé. Lorsqu'il
        # est fourni, il représente la feuille complète et remplace l'ancienne.
        if buteurs_data is not None:
            instance.buteurs.all().delete()
            ButeurMatch.objects.bulk_create(
                [ButeurMatch(match=instance, **buteur) for buteur in buteurs_data]
            )
        if participations_data is not None:
            instance.participations.all().delete()
            ParticipationMatch.objects.bulk_create(
                [ParticipationMatch(match=instance, **item) for item in participations_data]
            )

        # ``bulk_create`` ne déclenche pas de signal Django ; un recalcul final
        # après la feuille de match garantit des statistiques à jour.
        recalculer_classement(instance)
        recalculer_statistiques_competition(instance.competition)
        return instance


class ScoreDirectSerializer(serializers.Serializer):
    """Payload réduit et strict pour l'actualisation du score en direct."""

    score_domicile = serializers.IntegerField(min_value=0)
    score_exterieur = serializers.IntegerField(min_value=0)


class StatistiqueJoueurSerializer(serializers.ModelSerializer):
    joueur_nom = serializers.SerializerMethodField()
    joueur_photo = serializers.SerializerMethodField()
    poste = serializers.SerializerMethodField()

    class Meta:
        model = StatistiqueJoueur
        fields = [
            "id",
            "competition",
            "joueur",
            "joueur_nom",
            "joueur_photo",
            "poste",
            "matchs_joues",
            "buts",
            "passes_decisives",
            "cartons_jaunes",
            "cartons_rouges",
            "clean_sheets",
            "updated_at",
        ]
        read_only_fields = fields

    def get_joueur_nom(self, obj: StatistiqueJoueur) -> str:
        return str(obj.joueur)

    def get_joueur_photo(self, obj: StatistiqueJoueur) -> str | None:
        photo = getattr(obj.joueur, "photo", None)
        return photo.url if photo else None

    def get_poste(self, obj: StatistiqueJoueur) -> str | None:
        poste = getattr(obj.joueur, "poste", None)
        return getattr(poste, "nom", None)


class StatistiqueJoueurPublicSerializer(StatistiqueJoueurSerializer):
    """Alias explicite pour le contrat de lecture publique."""
