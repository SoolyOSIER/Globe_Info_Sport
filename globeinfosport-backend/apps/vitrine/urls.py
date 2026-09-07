"""Routes exposed through /api/v1/public/."""

from django.urls import path

from apps.actualites.views import (
    ArticlePublicDetailView,
    ArticlePublicListView,
    CitationPublicListView,
    ChiffreClePublicListView,
    VideoPublicListView,
)
from apps.competitions.views import (
    CalendrierPublicDownloadView,
    ClassementPublicView,
    ClubPublicListView,
    CompetitionPublicListView,
    MatchPublicDetailView,
    MatchPublicListView,
    StatistiquesPublicView,
)
from apps.expatries.views import JoueurExpatriePublicListView, TransfertPublicListView
from apps.galerie.views import AlbumGaleriePublicListView, ImageGaleriePublicListView
from apps.joueurs.views import JoueurPublicListView, LegendePublicListView

from .views import (
    PublicContactCreateView,
    PublicFAQListView,
    PublicNewsletterSubscriptionView,
    PublicNewsletterUnsubscribeView,
    PublicPageContenuListView,
    PublicPartenaireListView,
)

urlpatterns = [
    path("articles/", ArticlePublicListView.as_view()),
    path("articles/<slug:slug>/", ArticlePublicDetailView.as_view()),
    path("joueurs/", JoueurPublicListView.as_view()),
    path("legendes/", LegendePublicListView.as_view()),
    path("competitions/", CompetitionPublicListView.as_view()),
    path("clubs/", ClubPublicListView.as_view()),
    path("classement/<int:competition_id>/", ClassementPublicView.as_view()),
    path("matchs/calendrier/telecharger/", CalendrierPublicDownloadView.as_view()),
    path("matchs/", MatchPublicListView.as_view()),
    path("matchs/<int:pk>/", MatchPublicDetailView.as_view()),
    path("statistiques/<int:competition_id>/", StatistiquesPublicView.as_view()),
    path("expatries/", JoueurExpatriePublicListView.as_view()),
    path("transferts/", TransfertPublicListView.as_view()),
    path("galerie/", ImageGaleriePublicListView.as_view()),
    path("albums/", AlbumGaleriePublicListView.as_view()),
    path("chiffres-cles/", ChiffreClePublicListView.as_view()),
    path("videos/", VideoPublicListView.as_view()),
    path("citations/", CitationPublicListView.as_view()),
    path("faq/", PublicFAQListView.as_view()),
    path("partenaires/", PublicPartenaireListView.as_view()),
    path("pages/", PublicPageContenuListView.as_view()),
    path("contact/", PublicContactCreateView.as_view()),
    path("newsletter/abonnement/", PublicNewsletterSubscriptionView.as_view()),
    path("newsletter/desabonnement/<str:token>/", PublicNewsletterUnsubscribeView.as_view()),
]
