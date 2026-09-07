"""Deterministic reconstruction of player statistics from match events."""

from __future__ import annotations

from django.db import transaction
from django.db.models import Count, Q, Sum

from apps.competitions.models import (
    ButeurMatch,
    Competition,
    Match,
    ParticipationMatch,
    StatistiqueJoueur,
)


def recalculer_stats_joueur(match: Match) -> None:
    """Compatibility entry point used by match signals."""
    recalculer_statistiques_competition(match.competition)


def recalculer_statistiques_competition(competition: Competition) -> None:
    """Rebuild every statistic in a competition from completed match sheets."""
    buts = {
        row["joueur_id"]: row
        for row in ButeurMatch.objects.filter(
            match__competition=competition, match__statut=Match.Statut.TERMINE
        ).exclude(type_but=ButeurMatch.TypeBut.CSC).values("joueur_id").annotate(
            total=Count("id"), appearances=Count("match_id", distinct=True)
        )
    }
    passes = dict(
        ButeurMatch.objects.filter(
            match__competition=competition,
            match__statut=Match.Statut.TERMINE,
            passeur__isnull=False,
        ).values_list("passeur_id").annotate(total=Count("id"))
    )
    feuille = {
        row["joueur_id"]: row
        for row in ParticipationMatch.objects.filter(
            match__competition=competition, match__statut=Match.Statut.TERMINE
        ).values("joueur_id").annotate(
            appearances=Count("match_id", distinct=True),
            jaunes=Sum("cartons_jaunes"),
            rouges=Count("id", filter=Q(carton_rouge=True)),
            clean_sheets=Count("id", filter=Q(clean_sheet=True)),
        )
    }
    player_ids = set(buts) | set(passes) | set(feuille) | set(
        StatistiqueJoueur.objects.filter(competition=competition).values_list("joueur_id", flat=True)
    )
    with transaction.atomic():
        for player_id in player_ids:
            goal = buts.get(player_id, {})
            participation = feuille.get(player_id, {})
            stats, _ = StatistiqueJoueur.objects.get_or_create(
                competition=competition, joueur_id=player_id
            )
            stats.buts = goal.get("total", 0)
            stats.passes_decisives = passes.get(player_id, 0)
            stats.matchs_joues = participation.get("appearances", goal.get("appearances", 0))
            stats.cartons_jaunes = participation.get("jaunes") or 0
            stats.cartons_rouges = participation.get("rouges") or 0
            stats.clean_sheets = participation.get("clean_sheets") or 0
            stats.save(update_fields=[
                "buts", "passes_decisives", "matchs_joues", "cartons_jaunes",
                "cartons_rouges", "clean_sheets", "updated_at",
            ])
