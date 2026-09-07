"""Routes de l'API rédactionnelle des compétitions.

Les routes publiques sont centralisées dans ``apps.vitrine.urls`` pour que
toutes soient servies sous le préfixe ``/api/v1/public/``.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.competitions.views import (
    ClassementListView,
    CompetitionViewSet,
    ClubViewSet,
    MatchViewSet,
    StatistiqueJoueurListView,
)

app_name = "competitions"

router = DefaultRouter()
router.register("competitions", CompetitionViewSet, basename="competition")
router.register("clubs", ClubViewSet, basename="club")
router.register("matchs", MatchViewSet, basename="match")

urlpatterns = [
    path(
        "competitions/<int:competition_id>/classement/",
        ClassementListView.as_view(),
        name="competition-classement",
    ),
    path(
        "competitions/<int:competition_id>/statistiques/",
        StatistiqueJoueurListView.as_view(),
        name="competition-statistiques",
    ),
]
urlpatterns += router.urls
