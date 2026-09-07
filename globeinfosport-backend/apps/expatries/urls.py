"""Routes privées de gestion de la rubrique expatriés."""

from rest_framework.routers import DefaultRouter

from apps.expatries.views import ClubEtrangerViewSet, JoueurExpatrieViewSet, TransfertViewSet

app_name = "expatries"

router = DefaultRouter()
router.register("clubs-etrangers", ClubEtrangerViewSet, basename="club-etranger")
router.register("joueurs-expatries", JoueurExpatrieViewSet, basename="joueur-expatrie")
router.register("transferts", TransfertViewSet, basename="transfert")

urlpatterns = router.urls
