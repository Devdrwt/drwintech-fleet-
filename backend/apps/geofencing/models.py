from django.db import models


class Geofence(models.Model):
    name = models.CharField(max_length=120)
    client = models.ForeignKey(
        "crm.Client", on_delete=models.CASCADE, null=True, blank=True,
        related_name="geofences",
    )
    # GeoJSON (polygon ou circle). PostGIS envisageable en Phase 4.
    area = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class AlertRule(models.Model):
    class Type(models.TextChoices):
        ENTER = "enter", "Entrée zone"
        EXIT = "exit", "Sortie zone"
        OVERSPEED = "overspeed", "Excès de vitesse"
        LOW_BATTERY = "low_battery", "Batterie faible"
        SIM_LOW_BALANCE = "sim_low_balance", "Crédit SIM faible"

    geofence = models.ForeignKey(
        Geofence, on_delete=models.CASCADE, null=True, blank=True, related_name="rules"
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    threshold = models.FloatField(null=True, blank=True)
    channels = models.JSONField(default=list)  # ["email", "sms", "push"]
    is_active = models.BooleanField(default=True)


class AlertEvent(models.Model):
    rule = models.ForeignKey(
        AlertRule, on_delete=models.CASCADE, related_name="events"
    )
    device_imei = models.CharField(max_length=20, db_index=True)
    triggered_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(default=dict, blank=True)
    notified = models.BooleanField(default=False)
