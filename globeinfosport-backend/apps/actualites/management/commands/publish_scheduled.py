from django.core.management.base import BaseCommand
from apps.actualites.tasks import publier_articles_programmes


class Command(BaseCommand):
    help = "Publie les articles arrivés à échéance (alternative locale à Celery Beat)."

    def handle(self, *args, **options):
        self.stdout.write(f"{publier_articles_programmes()} article(s) publié(s).")
