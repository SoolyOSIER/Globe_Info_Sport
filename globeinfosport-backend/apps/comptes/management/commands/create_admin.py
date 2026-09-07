from __future__ import annotations

from getpass import getpass

from django.contrib.auth import password_validation
from django.core.management.base import BaseCommand, CommandError

from apps.comptes.models import RoleRedaction, Utilisateur


class Command(BaseCommand):
    help = "Crée le compte administrateur initial de la rédaction."

    def add_arguments(self, parser) -> None:  # type: ignore[no-untyped-def]
        parser.add_argument("--identifiant")
        parser.add_argument("--nom")
        parser.add_argument("--prenom", default="")
        parser.add_argument("--email", default="")
        parser.add_argument("--password")

    def handle(self, *args, **options):  # type: ignore[no-untyped-def]
        identifiant = options["identifiant"] or input("Identifiant : ").strip()
        nom = options["nom"] or input("Nom : ").strip()
        # Les champs facultatifs ont une valeur par défaut afin que la commande
        # reste compatible avec les scripts CI/non interactifs.
        prenom = options["prenom"]
        email = options["email"]

        if not identifiant or not nom:
            raise CommandError("L'identifiant et le nom sont obligatoires.")
        if Utilisateur.objects.filter(identifiant=identifiant).exists():
            raise CommandError("Cet identifiant existe déjà.")

        password = options["password"]
        if password is None:
            password = getpass("Mot de passe : ")
            confirmation = getpass("Confirmer le mot de passe : ")
            if password != confirmation:
                raise CommandError("Les mots de passe ne correspondent pas.")

        candidate = Utilisateur(
            identifiant=identifiant,
            nom=nom,
            prenom=prenom,
            email=email,
        )
        password_validation.validate_password(password, candidate)

        role, _ = RoleRedaction.objects.get_or_create(
            nomRole=RoleRedaction.NomRole.ADMINISTRATEUR,
        )
        Utilisateur.objects.create_superuser(
            identifiant=identifiant,
            password=password,
            nom=nom,
            prenom=prenom,
            email=email,
            role_redaction=role,
        )
        self.stdout.write(self.style.SUCCESS("Administrateur créé avec succès."))
