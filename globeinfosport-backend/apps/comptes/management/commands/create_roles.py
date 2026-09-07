from django.core.management.base import BaseCommand

from apps.comptes.models import RoleRedaction


class Command(BaseCommand):
    help = "Crée les rôles rédactionnels requis par Globe Info Sport."

    def handle(self, *args, **options):  # type: ignore[no-untyped-def]
        for role in RoleRedaction.NomRole.values:
            _, created = RoleRedaction.objects.get_or_create(nomRole=role)
            action = "créé" if created else "déjà présent"
            self.stdout.write(f"{role}: {action}")

        self.stdout.write(self.style.SUCCESS("Rôles rédactionnels prêts."))
