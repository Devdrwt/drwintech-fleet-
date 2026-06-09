"""
Services du contexte Fleet — orchestration métier hors des vues.
Le provisioning délègue à `integrations.traccar` (frontière unique du moteur).
"""
import logging

from django.utils import timezone

from apps.integrations.traccar import TraccarClient

from .models import GpsUnit

logger = logging.getLogger(__name__)


def provision_unit_on_traccar(unit: GpsUnit) -> GpsUnit:
    """
    Crée le device correspondant dans Traccar (uniqueId = imei) et stocke
    `traccar_device_id`. Idempotent : ne recrée pas si déjà lié.

    En cas d'échec moteur, on NE bloque PAS la création métier : l'unité reste
    créée avec `traccar_device_id` vide (à resynchroniser plus tard).
    """
    if unit.traccar_device_id:
        return unit
    try:
        device = TraccarClient().create_device(
            name=unit.serial_number or unit.imei, imei=unit.imei
        )
        unit.traccar_device_id = device.get("id")
        unit.last_synced_at = timezone.now()
        unit.save(update_fields=["traccar_device_id", "last_synced_at"])
        logger.info("GpsUnit %s provisionné sur Traccar (device %s)", unit.imei, unit.traccar_device_id)
    except Exception as exc:  # noqa: BLE001 — robustesse : l'échec moteur ne casse pas le métier
        logger.warning("Provisioning Traccar échoué pour %s : %s", unit.imei, exc)
    return unit


def deprovision_unit_on_traccar(unit: GpsUnit) -> None:
    """Supprime le device Traccar associé (best-effort)."""
    if not unit.traccar_device_id:
        return
    try:
        TraccarClient().delete_device(unit.traccar_device_id)
        logger.info("Device Traccar %s supprimé (unit %s)", unit.traccar_device_id, unit.imei)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Déprovisioning Traccar échoué pour %s : %s", unit.imei, exc)
