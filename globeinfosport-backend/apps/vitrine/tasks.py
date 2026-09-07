"""Asynchronous notifications from the public website."""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import AbonneNewsletter, MessageContact


@shared_task
def notifier_nouveau_message_contact(message_id: int) -> None:
    """Email the newsroom after a contact message is accepted."""
    message = MessageContact.objects.filter(pk=message_id).first()
    if not message:
        return
    recipients = [address for address in [getattr(settings, "CONTACT_RECIPIENT", "")] if address]
    if recipients:
        send_mail(
            subject=f"[Globe Info Sport] {message.sujet}",
            message=f"De : {message.nom} <{message.email}>\n\n{message.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )


@shared_task
def envoyer_bienvenue_newsletter(abonne_id: int) -> None:
    """Send one welcome message with a secure unsubscribe URL."""
    abonne = AbonneNewsletter.objects.filter(pk=abonne_id, actif=True).first()
    if not abonne:
        return
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    unsubscribe = f"{site_url}/newsletter/desabonnement/{abonne.token_desabonnement}" if site_url else ""
    send_mail(
        subject="Bienvenue sur Globe Info Sport",
        message=(
            "Merci de suivre Globe Info Sport, la passion du football haïtien.\n\n"
            f"Pour vous désabonner : {unsubscribe}" if unsubscribe else
            "Merci de suivre Globe Info Sport, la passion du football haïtien."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[abonne.email],
        fail_silently=False,
    )
