"""Erreurs métier et format d'erreur homogène de l'API."""

from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class BusinessRuleViolation(APIException):
    """Erreur levée lorsqu'une règle métier empêche une action."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cette action ne respecte pas une règle métier."
    default_code = "business_rule_violation"


class ResourceConflict(APIException):
    """Erreur pour une ressource incompatible avec l'état demandé."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "La ressource est en conflit avec son état actuel."
    default_code = "resource_conflict"


class InvalidTransition(BusinessRuleViolation):
    """Erreur dédiée aux changements de statut non autorisés."""

    default_detail = "Cette transition de statut n'est pas autorisée."
    default_code = "invalid_transition"


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Ajoute un statut lisible sans masquer le détail DRF d'origine."""

    response = drf_exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict):
        response.data.setdefault("status_code", response.status_code)
    return response
