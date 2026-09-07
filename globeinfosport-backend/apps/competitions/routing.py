"""Routes WebSocket optionnelles de l'application compétitions."""

from django.urls import path

from apps.competitions.consumers import MatchLiveConsumer


websocket_urlpatterns = [
    path("ws/matchs/<int:match_id>/", MatchLiveConsumer.as_asgi(), name="match-live"),
]
