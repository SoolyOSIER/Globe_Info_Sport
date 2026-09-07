"""Compatibilité des permissions comptes avec les composants transverses."""

from apps.core.permissions import (
    HIERARCHIE_ROLES,
    IsAdministrateur,
    IsEditeurOuPlus,
    IsRedacteurOuPlus,
    has_minimum_role,
)

# Nom conservé tel qu'il est prescrit dans le plan et utilisé côté React.
HIERARCHIE = HIERARCHIE_ROLES

__all__ = [
    "HIERARCHIE",
    "IsAdministrateur",
    "IsEditeurOuPlus",
    "IsRedacteurOuPlus",
    "has_minimum_role",
]
