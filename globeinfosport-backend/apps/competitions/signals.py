"""Déclencheurs d'automatisation liés aux résultats de match."""

from __future__ import annotations

from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.competitions.models import ButeurMatch, Match, ParticipationMatch
from apps.competitions.services import recalculer_classement, recalculer_statistiques_competition


def _recalculer_apres_validation(match_id: int) -> None:
    """Requête fraîche après commit afin de ne jamais calculer sur un rollback."""

    match = (
        Match.objects.select_related("competition", "club_domicile", "club_exterieur")
        .filter(pk=match_id)
        .first()
    )
    if (
        match is None
        or match.statut != Match.Statut.TERMINE
        or match.score_domicile is None
        or match.score_exterieur is None
    ):
        return
    recalculer_classement(match)
    recalculer_statistiques_competition(match.competition)
    cache.delete(f"classement:{match.competition_id}")
    cache.delete(f"stats:{match.competition_id}")


@receiver(post_save, sender=Match)
def match_termine_handler(sender, instance: Match, **kwargs) -> None:  # type: ignore[no-untyped-def]
    """Reconstruit les tableaux dès qu'un résultat final est enregistré."""

    if (
        instance.statut == Match.Statut.TERMINE
        and instance.score_domicile is not None
        and instance.score_exterieur is not None
    ):
        transaction.on_commit(lambda: _recalculer_apres_validation(instance.pk))


@receiver(post_save, sender=ButeurMatch)
@receiver(post_delete, sender=ButeurMatch)
@receiver(post_save, sender=ParticipationMatch)
@receiver(post_delete, sender=ParticipationMatch)
def buteur_match_modifie_handler(sender, instance: ButeurMatch, **kwargs) -> None:  # type: ignore[no-untyped-def]
    """Maintient les buts justes lors d'une correction d'événement isolé."""

    if instance.match_id:
        transaction.on_commit(lambda: _recalculer_apres_validation(instance.match_id))
