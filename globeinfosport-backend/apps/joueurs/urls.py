from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import JoueurViewSet, LegendeViewSet, PosteListView

router = DefaultRouter()
router.register("joueurs", JoueurViewSet, basename="joueur")
router.register("legendes", LegendeViewSet, basename="legende")

urlpatterns = [
    path("postes/", PosteListView.as_view(), name="poste-list"),
    path("", include(router.urls)),
]
