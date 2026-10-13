"""Permissions de rôle partagées par les ressources du back-office."""

from collections.abc import Iterable

from rest_framework.permissions import BasePermission


HIERARCHIE_ROLES: dict[str, int] = {
    "REDACTEUR": 1,
    "EDITEUR_EN_CHEF": 2,
    "ADMINISTRATEUR": 3,
}


def get_role_name(user: object) -> str | None:
    """Retourne le code du rôle sans échouer pour un visiteur anonyme.

    Les permissions sont utilisées très tôt dans le cycle DRF; cette fonction
    évite donc un ``RelatedObjectDoesNotExist`` ou un ``AttributeError`` pour
    une requête non authentifiée ou pour un compte incomplet.
    """

    if not getattr(user, "is_authenticated", False):
        return None

    role = getattr(user, "role_redaction", None)
    return getattr(role, "nomRole", None)


def has_minimum_role(user: object, role_minimum: str) -> bool:
    """Vérifie la hiérarchie cumulative des rôles rédactionnels."""

    if not getattr(user, "is_authenticated", False) or not getattr(user, "is_active", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    role = get_role_name(user)
    return HIERARCHIE_ROLES.get(role or "", 0) >= HIERARCHIE_ROLES[role_minimum]


class HasMinimumEditorialRole(BasePermission):
    """Permission paramétrable pour les rôles internes de la rédaction."""

    required_role = "REDACTEUR"

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        return has_minimum_role(request.user, self.required_role)


class IsRedacteurOuPlus(HasMinimumEditorialRole):
    """Autorise les rédacteurs, éditeurs en chef et administrateurs."""

    required_role = "REDACTEUR"


class IsEditeurOuPlus(HasMinimumEditorialRole):
    """Autorise les éditeurs en chef et administrateurs."""

    required_role = "EDITEUR_EN_CHEF"


class IsAdministrateur(HasMinimumEditorialRole):
    """Autorise uniquement les administrateurs de la rédaction."""

    required_role = "ADMINISTRATEUR"


class IsOwnerOrEditeurOuPlus(BasePermission):
    """Autorise un propriétaire ou un membre de l'équipe éditoriale senior.

    Cette permission est disponible pour les ressources qui requièrent une
    protection objet. Les ViewSets peuvent conserver des querysets filtrés en
    complément afin de ne jamais exposer un objet non autorisé.
    """

    owner_fields: Iterable[str] = ("auteur", "utilisateur", "owner")

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        return has_minimum_role(request.user, "REDACTEUR")

    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore[no-untyped-def]
        if has_minimum_role(request.user, "EDITEUR_EN_CHEF"):
            return True
        return any(
            getattr(obj, field, None) == request.user for field in self.owner_fields
        )
