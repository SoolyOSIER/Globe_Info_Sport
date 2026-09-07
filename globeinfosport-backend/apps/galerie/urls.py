"""Routes privées de gestion de la galerie."""

from rest_framework.routers import DefaultRouter

from apps.galerie.views import AlbumGalerieViewSet, ImageGalerieViewSet

app_name = "galerie"

router = DefaultRouter()
router.register("albums", AlbumGalerieViewSet, basename="album")
router.register("images", ImageGalerieViewSet, basename="image-galerie")

urlpatterns = router.urls
