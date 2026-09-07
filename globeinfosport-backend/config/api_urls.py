"""The authenticated editorial API and anonymous public API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.actualites.views import (
    ArticleViewSet,
    CategorieViewSet,
    ChiffreCleListView,
    CitationViewSet,
    TagViewSet,
    VideoViewSet,
)
from apps.competitions.views import (
    ClassementListView,
    ClubViewSet,
    CompetitionViewSet,
    MatchViewSet,
    StatistiqueJoueurListView,
)
from apps.comptes.views import (
    CookieTokenRefreshView,
    CurrentUserView,
    LoginView,
    LogoutView,
    UtilisateurViewSet,
)
from apps.expatries.views import ClubEtrangerViewSet, JoueurExpatrieViewSet, TransfertViewSet
from apps.galerie.views import AlbumGalerieViewSet, ImageGalerieViewSet
from apps.joueurs.views import JoueurViewSet, LegendeViewSet, PosteListView
from apps.vitrine.views import (
    AbonneNewsletterViewSet,
    FAQViewSet,
    MessageContactViewSet,
    PageContenuViewSet,
    PartenaireViewSet,
)

router = DefaultRouter()
router.register("utilisateurs", UtilisateurViewSet, basename="utilisateur")
router.register("articles", ArticleViewSet, basename="article")
router.register("categories", CategorieViewSet, basename="categorie")
router.register("tags", TagViewSet, basename="tag")
router.register("videos", VideoViewSet, basename="video")
router.register("citations", CitationViewSet, basename="citation")
router.register("joueurs", JoueurViewSet, basename="joueur")
router.register("legendes", LegendeViewSet, basename="legende")
router.register("competitions", CompetitionViewSet, basename="competition")
router.register("clubs", ClubViewSet, basename="club")
router.register("matchs", MatchViewSet, basename="match")
router.register("clubs-etrangers", ClubEtrangerViewSet, basename="club-etranger")
router.register("joueurs-expatries", JoueurExpatrieViewSet, basename="joueur-expatrie")
router.register("transferts", TransfertViewSet, basename="transfert")
router.register("albums", AlbumGalerieViewSet, basename="album")
router.register("images", ImageGalerieViewSet, basename="image")
router.register("messages-contact", MessageContactViewSet, basename="message-contact")
router.register("newsletter", AbonneNewsletterViewSet, basename="newsletter")
router.register("partenaires", PartenaireViewSet, basename="partenaire")
router.register("faq", FAQViewSet, basename="faq")
router.register("pages-contenu", PageContenuViewSet, basename="page-contenu")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", CurrentUserView.as_view(), name="current-user"),
    path("postes/", PosteListView.as_view(), name="poste-list"),
    path("chiffres-cles/", ChiffreCleListView.as_view(), name="chiffre-cle-list"),
    path(
        "competitions/<int:competition_id>/classement/",
        ClassementListView.as_view(),
        name="classement-list",
    ),
    path(
        "competitions/<int:competition_id>/statistiques/",
        StatistiqueJoueurListView.as_view(),
        name="statistique-list",
    ),
    path("public/", include("apps.vitrine.urls")),
    path("", include(router.urls)),
]
