from celery import shared_task

from .push import send_to_client

ALERT_TITLES = {
    "enter": "Entrée de zone",
    "exit": "Sortie de zone",
    "overspeed": "Excès de vitesse",
    "low_battery": "Batterie faible",
    "sim_low_balance": "Crédit SIM faible",
}


@shared_task
def push_alert_to_client(client_id: int, alert: dict):
    """Envoie une alerte en notification push au client concerné."""
    atype = alert.get("type", "")
    title = ALERT_TITLES.get(atype, "Alerte flotte")
    imei = alert.get("device_imei", "")
    payload = alert.get("payload", {})
    if atype == "overspeed":
        body = f"{imei} : {payload.get('speed')} km/h (seuil {payload.get('threshold')})"
    else:
        body = f"{imei} : {payload.get('geofence', '')}".strip()
    return send_to_client(client_id, title, body, {"url": "/client/alertes"})
