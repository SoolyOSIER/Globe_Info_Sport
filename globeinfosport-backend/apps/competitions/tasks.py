"""Tâches Celery de génération de calendrier et de rappel éditorial."""

from __future__ import annotations

from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import mail_admins
from django.db.models import QuerySet
from django.utils import timezone

from apps.competitions.models import Competition, Match
from apps.competitions.services import (
    FootballDataConfigurationError,
    FootballDataRequestError,
    synchroniser_football_data,
)

import logging


logger = logging.getLogger(__name__)


def _matches_calendrier(competition_id: int | None = None) -> QuerySet[Match]:
    queryset = Match.objects.select_related(
        "competition", "club_domicile", "club_exterieur"
    ).order_by("date_heure")
    if competition_id is not None:
        queryset = queryset.filter(competition_id=competition_id)
    return queryset


def build_calendrier_pdf(competition_id: int | None = None) -> BytesIO:
    """Construit en mémoire le PDF du calendrier et le renvoie au client."""

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
    except ImportError as exc:  # pragma: no cover - dépendance requise en production
        raise RuntimeError("ReportLab est requis pour générer le calendrier PDF.") from exc

    if competition_id is not None and not Competition.objects.filter(pk=competition_id).exists():
        raise Competition.DoesNotExist("Compétition introuvable.")

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    story = [Paragraph("Globe Info Sport — Calendrier des matchs", styles["Title"])]
    story.append(Spacer(1, 0.35 * cm))
    if competition_id:
        competition = Competition.objects.get(pk=competition_id)
        story.append(Paragraph(str(competition), styles["Heading2"]))
        story.append(Spacer(1, 0.2 * cm))

    rows: list[list[str]] = [["Date", "Compétition", "Affiche", "Lieu", "Statut"]]
    for match in _matches_calendrier(competition_id):
        adversaire = str(match.club_exterieur or match.adversaire_texte)
        rows.append(
            [
                timezone.localtime(match.date_heure).strftime("%d/%m/%Y %H:%M"),
                str(match.competition),
                f"{match.club_domicile} — {adversaire}",
                match.lieu or "—",
                match.get_statut_display(),
            ]
        )
    if len(rows) == 1:
        rows.append(["Aucun match programmé", "", "", "", ""])

    table = Table(rows, repeatRows=1, colWidths=[3 * cm, 4 * cm, 5.5 * cm, 3.5 * cm, 2.5 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00209f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    document.build(story)
    buffer.seek(0)
    return buffer


@shared_task
def generer_calendrier_pdf(competition_id: int | None = None) -> str:
    """Génère une copie téléchargeable du calendrier dans le stockage média."""

    pdf = build_calendrier_pdf(competition_id)
    suffix = f"competition-{competition_id}" if competition_id else "toutes-competitions"
    filename = f"calendriers/calendrier-{suffix}-{timezone.now():%Y%m%d%H%M%S}.pdf"
    return default_storage.save(filename, ContentFile(pdf.read()))


@shared_task
def rappel_match_a_venir() -> int:
    """Alerte la rédaction des matchs à préparer dans les prochaines 24 h."""

    maintenant = timezone.now()
    echeance = maintenant + timezone.timedelta(days=1)
    matchs = list(
        Match.objects.filter(
            statut=Match.Statut.A_VENIR,
            date_heure__gte=maintenant,
            date_heure__lte=echeance,
        )
        .select_related("competition", "club_domicile", "club_exterieur")
        .order_by("date_heure")
    )
    if not matchs:
        return 0

    lignes = []
    for match in matchs:
        adversaire = match.club_exterieur or match.adversaire_texte
        lignes.append(
            f"- {match.date_heure:%d/%m/%Y %H:%M} : "
            f"{match.club_domicile} — {adversaire} ({match.competition})"
        )
    mail_admins(
        "Globe Info Sport — matchs à préparer",
        "Matchs programmés dans les prochaines 24 heures :\n\n" + "\n".join(lignes),
        fail_silently=not settings.DEBUG,
    )
    return len(matchs)


@shared_task
def synchroniser_football_automatique() -> dict[str, int | bool]:
    """Actualise les compétitions connectées quand une clé fournisseur est définie."""

    if not settings.FOOTBALL_DATA_API_TOKEN:
        return {"configured": False}
    try:
        return {"configured": True, **synchroniser_football_data()}
    except (FootballDataConfigurationError, FootballDataRequestError, ValueError):
        logger.exception("La synchronisation football-data.org a échoué.")
        raise
