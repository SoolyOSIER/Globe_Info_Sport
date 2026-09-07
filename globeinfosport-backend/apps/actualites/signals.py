from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Article
from .tasks import envoyer_digest_newsletter


@receiver(pre_save, sender=Article)
def memoriser_statut_precedent(sender, instance: Article, raw: bool = False, **kwargs) -> None:
    """Mémorise le statut antérieur pour détecter une première publication."""

    if raw or not instance.pk:
        instance._statut_precedent = None
        return
    instance._statut_precedent = (
        sender.objects.filter(pk=instance.pk).values_list("statut", flat=True).first()
    )


@receiver(post_save, sender=Article)
def programmer_digest_apres_publication(
    sender,
    instance: Article,
    created: bool,
    raw: bool = False,
    **kwargs,
) -> None:
    """Déclenche une notification lorsqu'un article franchit l'étape publié."""

    previous_status = getattr(instance, "_statut_precedent", None)
    if (
        not raw
        and instance.statut == Article.Statut.PUBLIE
        and (created or previous_status != Article.Statut.PUBLIE)
    ):
        transaction.on_commit(lambda: envoyer_digest_newsletter.delay())
