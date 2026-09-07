"""Support optionnel Django Channels pour les scores en direct."""

from __future__ import annotations

import json
from typing import Any

try:  # Channels est optionnel au lancement (polling REST reste disponible).
    from asgiref.sync import async_to_sync
    from channels.generic.websocket import AsyncWebsocketConsumer
    from channels.layers import get_channel_layer
except ImportError:  # pragma: no cover - dépend de l'installation optionnelle
    AsyncWebsocketConsumer = None  # type: ignore[assignment,misc]
    async_to_sync = None  # type: ignore[assignment]
    get_channel_layer = None  # type: ignore[assignment]


if AsyncWebsocketConsumer is not None:

    class MatchLiveConsumer(AsyncWebsocketConsumer):
        """Abonne les visiteurs au groupe WebSocket d'un match précis."""

        async def connect(self) -> None:
            self.match_id = self.scope["url_route"]["kwargs"]["match_id"]
            self.group_name = f"match_{self.match_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

        async def disconnect(self, close_code: int) -> None:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

        async def score_update(self, event: dict[str, Any]) -> None:
            await self.send(text_data=json.dumps(event["data"]))

else:

    class MatchLiveConsumer:  # pragma: no cover - protection de l'import optionnel
        """Place-holder explicite si Django Channels n'est pas installé."""

        @classmethod
        def as_asgi(cls):
            raise RuntimeError("Django Channels doit être installé pour activer le WebSocket.")


def diffuser_score_live(match) -> bool:  # type: ignore[no-untyped-def]
    """Diffuse un nouveau score si un channel layer est configuré.

    La mise à jour REST ne doit jamais échouer uniquement parce que Channels
    n'est pas encore activé ; la fonction retourne donc ``False`` dans ce cas.
    """

    if get_channel_layer is None or async_to_sync is None:
        return False
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return False
    adversaire = str(match.club_exterieur or match.adversaire_texte)
    payload = {
        "id": match.pk,
        "club_domicile": str(match.club_domicile),
        "club_exterieur": adversaire,
        "score_domicile": match.score_domicile,
        "score_exterieur": match.score_exterieur,
        "statut": match.statut,
        "updated_at": match.updated_at.isoformat() if match.updated_at else None,
    }
    async_to_sync(channel_layer.group_send)(
        f"match_{match.pk}", {"type": "score.update", "data": payload}
    )
    return True
