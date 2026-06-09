"""
Client de l'API REST Traccar — frontière unique avec le moteur d'ingestion.
Tout le reste du code passe par ici (voir ADR 0001 / ARCHITECTURE.md).
Si on change un jour de moteur, seul ce fichier est impacté.
"""
import httpx
from django.conf import settings


class TraccarClient:
    def __init__(self):
        self.base_url = settings.TRACCAR_API_URL.rstrip("/")
        self.auth = (settings.TRACCAR_SERVICE_USER, settings.TRACCAR_SERVICE_PASSWORD)

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, auth=self.auth, timeout=15)

    # --- Devices (provisioning) ---
    def create_device(self, name: str, imei: str) -> dict:
        """Crée un device Traccar (uniqueId = imei). Retourne le device créé."""
        with self._client() as c:
            r = c.post("/devices", json={"name": name, "uniqueId": imei})
            r.raise_for_status()
            return r.json()

    def list_devices(self) -> list[dict]:
        with self._client() as c:
            r = c.get("/devices")
            r.raise_for_status()
            return r.json()

    def delete_device(self, device_id: int) -> None:
        with self._client() as c:
            r = c.delete(f"/devices/{device_id}")
            r.raise_for_status()

    # --- Commandes sortantes (action sensible — auditée côté appelant) ---
    def send_command(self, device_id: int, command_type: str, **attributes) -> dict:
        with self._client() as c:
            payload = {"deviceId": device_id, "type": command_type, "attributes": attributes}
            r = c.post("/commands/send", json=payload)
            r.raise_for_status()
            return r.json()
