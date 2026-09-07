from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Utilisateur
from .tasks import send_welcome_email


@receiver(post_save, sender=Utilisateur)
def envoyer_bienvenue_nouvel_utilisateur(
    sender,
    instance: Utilisateur,
    created: bool,
    raw: bool = False,
    **kwargs,
) -> None:
    """Programme l'accueil seulement quand la transaction est validée."""

    if created and not raw and instance.email:
        transaction.on_commit(lambda: send_welcome_email.delay(instance.pk))
