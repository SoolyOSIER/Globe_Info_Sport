from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ArticleViewSet,
    CategorieViewSet,
    ChiffreCleListView,
    CitationViewSet,
    TagViewSet,
    VideoViewSet,
)

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="article")
router.register("categories", CategorieViewSet, basename="categorie")
router.register("tags", TagViewSet, basename="tag")
router.register("videos", VideoViewSet, basename="video")
router.register("citations", CitationViewSet, basename="citation")

urlpatterns = [
    path("chiffres-cles/", ChiffreCleListView.as_view(), name="chiffre-cle-list"),
    path("", include(router.urls)),
]
