from django.core.management.base import BaseCommand, CommandError

from apps.competitions.services import (
    FootballDataConfigurationError,
    FootballDataRequestError,
    synchroniser_football_data,
)


class Command(BaseCommand):
    help = "Synchronise équipes, calendrier, résultats et classement depuis football-data.org."

    def add_arguments(self, parser):
        parser.add_argument(
            "--competition",
            action="append",
            dest="competitions",
            help="Code football-data.org à synchroniser (PL, PD, SA, BL1 ou FL1). Répétez l'option si nécessaire.",
        )

    def handle(self, *args, **options):
        try:
            resume = synchroniser_football_data(options["competitions"])
        except (FootballDataConfigurationError, FootballDataRequestError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            self.style.SUCCESS(
                "Synchronisation terminée : "
                f"{resume['competitions']} compétitions, {resume['equipes']} nouvelles équipes, "
                f"{resume['matchs']} matchs et {resume['lignes_classement']} lignes de classement."
            )
        )
