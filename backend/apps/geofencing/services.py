"""
Évaluation des règles d'alerte sur une position (appelée par le WS Bridge).

Formats de zone supportés (Geofence.area) :
  - cercle  : {"type": "circle", "lat": 6.37, "lon": 2.42, "radius_m": 1000}
  - polygone: {"type": "polygon", "points": [[lat, lon], [lat, lon], ...]}

La détection entrée/sortie est transitionnelle : elle compare l'état courant
(dans/hors zone) à l'état précédent, fourni par l'appelant (dict mutable).
"""
import math

from .models import AlertEvent, AlertRule


def _haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _point_in_polygon(lat, lon, points):
    """Ray casting. points = [[lat, lon], ...]."""
    inside = False
    n = len(points)
    j = n - 1
    for i in range(n):
        yi, xi = points[i][0], points[i][1]
        yj, xj = points[j][0], points[j][1]
        if ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


def point_in_geofence(lat, lon, area: dict) -> bool:
    if not area:
        return False
    kind = area.get("type")
    if kind == "circle":
        return _haversine_m(lat, lon, area["lat"], area["lon"]) <= area["radius_m"]
    if kind == "polygon":
        return _point_in_polygon(lat, lon, area.get("points", []))
    return False


def evaluate_and_record(imei: str, lat: float, lon: float, speed: float, state: dict):
    """
    Évalue les règles actives, enregistre les AlertEvent déclenchés et
    renvoie la liste des alertes (dicts sérialisables) pour diffusion.
    `state` : dict mutable conservé par l'appelant entre les positions.
    """
    triggered = []
    rules = AlertRule.objects.filter(is_active=True).select_related("geofence")
    for rule in rules:
        if rule.type in (AlertRule.Type.ENTER, AlertRule.Type.EXIT) and rule.geofence:
            inside = point_in_geofence(lat, lon, rule.geofence.area)
            key = (imei, "gf", rule.geofence_id)
            was = state.get(key)
            state[key] = inside
            if was is None:
                continue  # première observation : pas de transition
            entered = (not was) and inside
            exited = was and (not inside)
            if (rule.type == AlertRule.Type.ENTER and entered) or (
                rule.type == AlertRule.Type.EXIT and exited
            ):
                triggered.append(
                    _record(rule, imei, {"lat": lat, "lon": lon, "geofence": rule.geofence.name})
                )
        elif rule.type == AlertRule.Type.OVERSPEED and rule.threshold is not None:
            key = (imei, "ovs", rule.id)
            was_over = state.get(key, False)
            now_over = speed > rule.threshold
            state[key] = now_over
            if now_over and not was_over:  # transition sous->sur le seuil
                triggered.append(
                    _record(rule, imei, {"speed": speed, "threshold": rule.threshold})
                )
    return triggered


def _record(rule, imei, payload) -> dict:
    event = AlertEvent.objects.create(
        rule=rule, device_imei=imei, payload=payload, notified=False
    )
    return {
        "id": event.id,
        "type": rule.type,
        "device_imei": imei,
        "payload": payload,
    }
