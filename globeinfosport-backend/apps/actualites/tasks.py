from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F, Sum
from django.utils import timezone

from .models import Article, ChiffreCle


def _calculer_valeur(code: str) -> int | None:
    """Retourne une valeur métier pour un code de chiffre clé connu."""

    if code == "NB_ARTICLES_PUBLIES":
        return Article.objects.filter(statut=Article.Statut.PUBLIE).count()

    if code in {"NB_SELECTIONS_TOTAL", "NB_BUTS_SELECTION", "NB_JOUEURS_SELECTION"}:
        joueur_model = apps.get_model("joueurs", "Joueur")
        if code == "NB_SELECTIONS_TOTAL":
            return joueur_model.objects.aggregate(total=Sum("nb_selections"))["total"] or 0
        if code == "NB_BUTS_SELECTION":
            return (
                joueur_model.objects.aggregate(total=Sum("nb_buts_selection"))["total"]
                or 0
            )
        return joueur_model.objects.filter(selection_nationale=True).count()

    if code in {"NB_VICTOIRES_SAISON", "NB_MATCHS_TERMINES"}:
        match_model = apps.get_model("competitions", "Match")
        queryset = match_model.objects.filter(statut="TERMINE")
        if code == "NB_MATCHS_TERMINES":
            return queryset.count()
        return queryset.exclude(score_domicile=F("score_exterieur")).count()

    return None


@shared_task
def recalculer_chiffres_cles() -> int:
    """Met à jour les indicateurs automatiques de la page Actualités.

    Les valeurs restent des chaînes pour permettre une présentation localisée,
    mais toutes les sources de vérité sont des tables métier.
    """

    updated = 0
    for chiffre in ChiffreCle.objects.filter(calcule_auto=True):
        valeur = _calculer_valeur(chiffre.code_calcul)
        if valeur is None:
            continue
        valeur_formatee = str(valeur)
        if chiffre.valeur != valeur_formatee:
            chiffre.valeur = valeur_formatee
            chiffre.save(update_fields=["valeur"])
            updated += 1
    return updated


@shared_task
def envoyer_digest_newsletter() -> int:
    """Envoie aux abonnés actifs les articles publiés dans les dernières 24 h."""

    newsletter_model = apps.get_model("vitrine", "AbonneNewsletter")
    since = timezone.now() - timedelta(days=1)
    articles = list(
        Article.objects.filter(
            statut=Article.Statut.PUBLIE,
            date_publication__gte=since,
        ).order_by("-date_publication")
    )
    if not articles:
        return 0

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    lines = ["Les dernières nouvelles de Globe Info Sport :", ""]
    for article in articles:
        url = f"{site_url}/actualites/{article.slug}" if site_url else article.titre
        lines.extend([article.titre, article.chapo, url, ""])
    message = "\n".join(lines)

    sent = 0
    for abonne in newsletter_model.objects.filter(actif=True).iterator():
        unsubscribe_url = ""
        if site_url:
            unsubscribe_url = (
                f"\nPour vous désabonner : {site_url}/newsletter/desabonnement/"
                f"{abonne.token_desabonnement}"
            )
        send_mail(
            subject="Globe Info Sport — vos actualités football",
            message=message + unsubscribe_url,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[abonne.email],
            fail_silently=False,
        )
        sent += 1
    return sent
