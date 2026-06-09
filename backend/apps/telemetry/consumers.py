import json

from channels.generic.websocket import AsyncWebsocketConsumer


class LivePositionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket carte temps réel.
    Le client s'abonne aux positions ; le WS Bridge publie via le channel layer
    (groupe `positions`) les positions reçues de Traccar.
    """

    GROUP = "positions"

    async def connect(self):
        # TODO Phase 2 : authentifier le token JWT depuis la query string.
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    async def position_update(self, event):
        """Handler appelé par group_send(type='position_update')."""
        await self.send(text_data=json.dumps(event["data"]))
