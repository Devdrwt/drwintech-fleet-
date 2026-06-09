import json

from channels.generic.websocket import AsyncWebsocketConsumer


def _group_for(base: str, user) -> str:
    """Groupe global pour le back-office, groupe par client sinon (cloisonnement)."""
    client_id = getattr(user, "client_id", None)
    return f"{base}_client_{client_id}" if client_id else base


class LivePositionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket carte temps réel.
    - Back-office (sans client) : groupe global `positions` (toutes les balises).
    - Client : groupe `positions_client_<id>` (uniquement ses balises).
    """

    async def connect(self):
        # Auth JWT via JWTAuthMiddleware (?token=). Rejet si non authentifié.
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4001)
            return
        self.group = _group_for("positions", user)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def position_update(self, event):
        """Handler appelé par group_send(type='position_update')."""
        await self.send(text_data=json.dumps(event["data"]))


class AlertConsumer(AsyncWebsocketConsumer):
    """WebSocket des alertes (géofences, excès de vitesse), cloisonné par client."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4001)
            return
        self.group = _group_for("alerts", user)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def alert_event(self, event):
        """Handler appelé par group_send(type='alert_event')."""
        await self.send(text_data=json.dumps(event["data"]))
