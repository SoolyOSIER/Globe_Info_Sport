"""Limiteurs explicites pour les endpoints anonymes de la vitrine."""

from rest_framework.throttling import ScopedRateThrottle


class PublicWriteThrottle(ScopedRateThrottle):
    """Applique le scope ``public`` : 20 requêtes par heure et par IP."""

    scope = "public"


class PublicReadThrottle(ScopedRateThrottle):
    """Applique le scope ``public-read`` : 300 requêtes par heure et par IP."""

    scope = "public-read"


# Nom conservé pour la convention annoncée dans l'arborescence du plan.
PublicAnonThrottle = PublicWriteThrottle
