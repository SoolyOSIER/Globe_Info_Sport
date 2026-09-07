from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CookieTokenRefreshView,
    CurrentUserView,
    LoginView,
    LogoutView,
    UtilisateurViewSet,
)

router = DefaultRouter()
router.register("utilisateurs", UtilisateurViewSet, basename="utilisateur")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("", include(router.urls)),
]
