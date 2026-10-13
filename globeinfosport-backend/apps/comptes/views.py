from __future__ import annotations

from django.conf import settings
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Utilisateur, RoleRedaction
from .permissions import IsAdministrateur
from .serializers import (
    UtilisateurCreateSerializer,
    UtilisateurSerializer,
    UtilisateurUpdateSerializer,
    RoleRedactionSerializer,
)


def _refresh_cookie_options() -> dict[str, object]:
    """Centralise les attributs du cookie refresh, sûrs aussi en développement."""

    return {
        "httponly": True,
        "secure": getattr(settings, "JWT_REFRESH_COOKIE_SECURE", not settings.DEBUG),
        "samesite": getattr(settings, "JWT_REFRESH_COOKIE_SAMESITE", "Lax"),
        "max_age": int(
            getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 7 * 24 * 60 * 60)
        ),
        "path": getattr(settings, "JWT_REFRESH_COOKIE_PATH", "/api/v1/auth/"),
    }


class LoginView(TokenObtainPairView):
    """Émet l'access token JSON et place le refresh token dans un cookie httpOnly."""

    def post(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        response = super().post(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return response

        refresh = response.data.pop("refresh", None)
        identifiant = request.data.get("identifiant")
        utilisateur = Utilisateur.objects.select_related("role_redaction").get(
            identifiant=identifiant
        )
        utilisateur.dernier_acces = timezone.now()
        utilisateur.save(update_fields=["dernier_acces"])

        response.data["user"] = UtilisateurSerializer(
            utilisateur,
            context={"request": request},
        ).data
        if refresh:
            response.set_cookie("refresh_token", refresh, **_refresh_cookie_options())
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Accepte un refresh HTTP-only sans l'exposer au JavaScript de la SPA."""

    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        refresh_token = request.data.get("refresh") or request.COOKIES.get(
            "refresh_token"
        )
        if not refresh_token:
            raise ValidationError({"refresh": "Le jeton de rafraîchissement est requis."})

        serializer = self.get_serializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        rotated_refresh = serializer.validated_data.get("refresh")
        if rotated_refresh:
            response.set_cookie(
                "refresh_token",
                rotated_refresh,
                **_refresh_cookie_options(),
            )
        return response


@extend_schema(request=None, responses={204: None})
class LogoutView(APIView):
    """Révoque le refresh HTTP-only et retire son cookie du navigateur."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                # Un cookie expiré ou déjà révoqué reste un logout réussi.
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
            "refresh_token",
            path=getattr(settings, "JWT_REFRESH_COOKIE_PATH", "/api/v1/auth/"),
            samesite=getattr(settings, "JWT_REFRESH_COOKIE_SAMESITE", "Lax"),
        )
        return response


@extend_schema(responses=UtilisateurSerializer)
class CurrentUserView(APIView):
    """Retourne le profil du membre connecté pour restaurer la session SPA."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        return Response(UtilisateurSerializer(request.user, context={"request": request}).data)


class RoleRedactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RoleRedaction.objects.all()
    serializer_class = RoleRedactionSerializer
    permission_classes = [IsAdministrateur]


class UtilisateurViewSet(viewsets.ModelViewSet):
    """Administration des comptes internes, réservée aux administrateurs."""

    queryset = Utilisateur.objects.select_related("role_redaction").all()
    permission_classes = [IsAdministrateur]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["role_redaction", "is_active"]
    search_fields = ["identifiant", "nom", "prenom", "email"]
    ordering_fields = ["nom", "prenom", "identifiant", "date_creation_compte"]
    ordering = ["nom", "prenom", "identifiant"]

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "create":
            return UtilisateurCreateSerializer
        if self.action in {"update", "partial_update"}:
            return UtilisateurUpdateSerializer
        return UtilisateurSerializer

    def destroy(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        instance = self.get_object()
        if instance.pk == request.user.pk:
            raise ValidationError(
                {"detail": "Vous ne pouvez pas supprimer votre propre compte."}
            )
        return super().destroy(request, *args, **kwargs)
