from __future__ import annotations

from urllib.parse import quote

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


@shared_task(ignore_result=True)
def send_welcome_email(utilisateur_id: int) -> bool:
    """Envoie l'email de bienvenue après la création d'un compte interne."""

    user_model = get_user_model()
    try:
        utilisateur = user_model.objects.get(pk=utilisateur_id)
    except user_model.DoesNotExist:
        return False

    if not utilisateur.email:
        return False

    role = utilisateur.role_redaction.get_nomRole_display()
    send_mail(
        subject="Bienvenue dans la rédaction Globe Info Sport",
        message=(
            f"Bonjour {utilisateur.get_short_name()},\n\n"
            "Votre compte de rédaction Globe Info Sport est prêt.\n"
            f"Identifiant : {utilisateur.identifiant}\n"
            f"Rôle : {role}\n"
        ),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[utilisateur.email],
        fail_silently=False,
    )
    return True


@shared_task(ignore_result=True)
def send_password_reset_email(utilisateur_id: int, token: str) -> bool:
    """Envoie un lien de réinitialisation préparé par le flux d'authentification."""

    user_model = get_user_model()
    try:
        utilisateur = user_model.objects.get(pk=utilisateur_id)
    except user_model.DoesNotExist:
        return False

    if not utilisateur.email:
        return False

    template = getattr(settings, "PASSWORD_RESET_URL", "")
    reset_url = template.format(token=quote(token)) if template else ""
    send_mail(
        subject="Réinitialisation de votre mot de passe Globe Info Sport",
        message=(
            "Une réinitialisation de mot de passe a été demandée pour votre "
            "compte de rédaction.\n\n"
            f"{reset_url}" if reset_url else "Contactez un administrateur pour réinitialiser votre mot de passe."
        ),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[utilisateur.email],
        fail_silently=False,
    )
    return True
