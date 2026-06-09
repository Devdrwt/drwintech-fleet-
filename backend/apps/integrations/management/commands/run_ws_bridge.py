"""
WS Bridge — pont entre le moteur Traccar et la plateforme.

Boucle :
  1. S'authentifie auprès de Traccar (/api/session) pour obtenir un cookie.
  2. Se connecte au WebSocket Traccar (/api/socket).
  3. Pour chaque position reçue :
       - persiste dans TimescaleDB (telemetry.Position),
       - diffuse au front via le channel layer (groupe `positions`),
         consommé par telemetry.consumers.LivePositionConsumer.

Mapping device : Traccar identifie par `deviceId` (int) ; on résout vers
l'IMEI métier via fleet.GpsUnit.traccar_device_id. Le mapping est rafraîchi
au démarrage et à chaque deviceId inconnu.

Lancement :  python manage.py run_ws_bridge
"""
import asyncio
import json

import httpx
import websockets
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

GROUP = "positions"


class Command(BaseCommand):
    help = "Démarre le pont WebSocket Traccar -> Redis/Channels + TimescaleDB."

    def handle(self, *args, **options):
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            self.stdout.write("Arrêt du WS Bridge.")

    async def _run(self):
        channel_layer = get_channel_layer()
        backoff = 1
        while True:
            try:
                cookie = await self._login()
                device_map = await self._load_device_map()
                ws_url = settings.TRACCAR_WS_URL
                self.stdout.write(self.style.SUCCESS(f"Connexion WS Traccar : {ws_url}"))
                async with websockets.connect(
                    ws_url, additional_headers={"Cookie": cookie}
                ) as ws:
                    backoff = 1
                    async for raw in ws:
                        await self._handle_message(raw, device_map, channel_layer)
            except Exception as exc:  # noqa: BLE001 — boucle résiliente : on relogue et on retente
                self.stderr.write(f"WS Bridge erreur : {exc} — reconnexion dans {backoff}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)

    async def _login(self) -> str:
        """Authentifie le compte de service et renvoie l'en-tête Cookie."""
        async with httpx.AsyncClient(base_url=settings.TRACCAR_API_URL, timeout=15) as c:
            r = await c.post(
                "/session",
                data={
                    "email": settings.TRACCAR_SERVICE_USER,
                    "password": settings.TRACCAR_SERVICE_PASSWORD,
                },
            )
            r.raise_for_status()
            jsession = r.cookies.get("JSESSIONID")
            return f"JSESSIONID={jsession}"

    @sync_to_async
    def _load_device_map(self) -> dict:
        """Mapping {traccar_device_id: imei} depuis le parc."""
        from apps.fleet.models import GpsUnit

        return {
            u.traccar_device_id: u.imei
            for u in GpsUnit.objects.exclude(traccar_device_id__isnull=True)
        }

    async def _handle_message(self, raw, device_map, channel_layer):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return
        positions = data.get("positions") or []
        for pos in positions:
            device_id = pos.get("deviceId")
            imei = device_map.get(device_id)
            if imei is None:
                # Device inconnu : on rafraîchit le mapping une fois.
                device_map.update(await self._load_device_map())
                imei = device_map.get(device_id)
                if imei is None:
                    continue
            await self._persist_position(imei, pos)
            await channel_layer.group_send(
                GROUP,
                {
                    "type": "position_update",
                    "data": {
                        "device_imei": imei,
                        "latitude": pos.get("latitude"),
                        "longitude": pos.get("longitude"),
                        "speed": pos.get("speed", 0),
                        "course": pos.get("course", 0),
                        "fixTime": pos.get("fixTime"),
                    },
                },
            )

    @sync_to_async
    def _persist_position(self, imei: str, pos: dict):
        from apps.telemetry.models import Position

        Position.objects.create(
            time=parse_datetime(pos["fixTime"]) if pos.get("fixTime") else None,
            device_imei=imei,
            latitude=pos.get("latitude", 0),
            longitude=pos.get("longitude", 0),
            speed=pos.get("speed", 0),
            course=pos.get("course", 0),
            altitude=pos.get("altitude", 0),
            attributes=pos.get("attributes", {}),
        )
