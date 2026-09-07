"""Signals dispatch only one notification per newly created public record."""

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AbonneNewsletter, MessageContact
from .tasks import envoyer_bienvenue_newsletter, notifier_nouveau_message_contact


@receiver(post_save, sender=MessageContact)
def message_contact_created(sender, instance: MessageContact, created: bool, **kwargs) -> None:
    if created:
        transaction.on_commit(lambda: notifier_nouveau_message_contact.delay(instance.pk))


@receiver(post_save, sender=AbonneNewsletter)
def newsletter_created(sender, instance: AbonneNewsletter, created: bool, **kwargs) -> None:
    if created:
        transaction.on_commit(lambda: envoyer_bienvenue_newsletter.delay(instance.pk))
