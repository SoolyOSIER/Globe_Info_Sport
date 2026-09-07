from __future__ import annotations

from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models


class RoleRedaction(models.Model):
    """Rôle hiérarchique attribué à un membre de la rédaction."""

    class NomRole(models.TextChoices):
        REDACTEUR = "REDACTEUR", "Rédacteur"
        EDITEUR_EN_CHEF = "EDITEUR_EN_CHEF", "Éditeur en chef"
        ADMINISTRATEUR = "ADMINISTRATEUR", "Administrateur"

    nomRole = models.CharField(
        max_length=30,
        unique=True,
        choices=NomRole.choices,
    )

    class Meta:
        verbose_name = "rôle de rédaction"
        verbose_name_plural = "rôles de rédaction"
        ordering = ["nomRole"]

    def __str__(self) -> str:
        return self.get_nomRole_display()


class UtilisateurManager(BaseUserManager):
    """Manager du modèle utilisateur basé sur l'identifiant rédactionnel."""

    use_in_migrations = True

    def _create_user(
        self,
        identifiant: str,
        password: str | None,
        **extra_fields: Any,
    ) -> "Utilisateur":
        if not identifiant:
            raise ValueError("L'identifiant est obligatoire.")
        if password is None:
            raise ValueError("Le mot de passe est obligatoire.")

        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)

        user = self.model(identifiant=identifiant.strip(), **extra_fields)
        user.set_password(password)
        user.full_clean(exclude=["role_redaction"])
        user.save(using=self._db)
        return user

    def create_user(
        self,
        identifiant: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "Utilisateur":
        """Crée un membre actif de la rédaction avec un rôle explicite."""

        if not extra_fields.get("role_redaction"):
            raise ValueError("Un rôle de rédaction est obligatoire.")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(identifiant, password, **extra_fields)

    def create_superuser(
        self,
        identifiant: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "Utilisateur":
        """Crée un administrateur Django et un administrateur éditorial."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("nom", identifiant)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superutilisateur doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superutilisateur doit avoir is_superuser=True.")

        role = extra_fields.get("role_redaction")
        if role is None:
            role, _ = RoleRedaction.objects.get_or_create(
                nomRole=RoleRedaction.NomRole.ADMINISTRATEUR,
            )
            extra_fields["role_redaction"] = role

        return self._create_user(identifiant, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """Compte interne de Globe Info Sport; aucun visiteur n'en possède."""

    identifiant = models.CharField(max_length=150, unique=True)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to="redaction/", null=True, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    date_creation_compte = models.DateTimeField(auto_now_add=True)
    dernier_acces = models.DateTimeField(null=True, blank=True)

    role_redaction = models.ForeignKey(
        RoleRedaction,
        on_delete=models.PROTECT,
        related_name="utilisateurs",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UtilisateurManager()

    USERNAME_FIELD = "identifiant"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        ordering = ["nom", "prenom", "identifiant"]

    def __str__(self) -> str:
        return self.get_full_name() or self.identifiant

    def get_full_name(self) -> str:
        """Retourne le nom d'affichage sans espaces résiduels."""

        return f"{self.prenom} {self.nom}".strip()

    def get_short_name(self) -> str:
        return self.prenom or self.identifiant

    @property
    def role_code(self) -> str | None:
        """Expose le code de rôle utile aux permissions et aux clients API."""

        if not self.role_redaction_id:
            return None
        return self.role_redaction.nomRole

    def clean(self) -> None:
        super().clean()
        if self.identifiant:
            self.identifiant = self.identifiant.strip()
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)

        if self.is_superuser and self.role_redaction_id:
            if self.role_redaction.nomRole != RoleRedaction.NomRole.ADMINISTRATEUR:
                raise ValidationError(
                    {"role_redaction": "Un superutilisateur doit être administrateur."}
                )
