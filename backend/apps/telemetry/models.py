from django.db import models

# Ces modèles vivent dans la base TimescaleDB (routeur — voir ADR 0003).
# Pas de FK vers le métier : la liaison se fait par IMEI (device_imei).


class Position(models.Model):
    """Position brute. Convertie en hypertable Timescale via migration SQL."""

    time = models.DateTimeField(db_index=True)
    device_imei = models.CharField(max_length=20, db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed = models.FloatField(default=0)
    course = models.FloatField(default=0)
    altitude = models.FloatField(default=0)
    attributes = models.JSONField(default=dict, blank=True)

    class Meta:
        # Hypertable : clé composite gérée par Timescale, pas d'autopk classique.
        indexes = [models.Index(fields=["device_imei", "time"])]
        managed = True

    def __str__(self):
        return f"{self.device_imei} @ {self.time}"


class DeviceEvent(models.Model):
    time = models.DateTimeField(db_index=True)
    device_imei = models.CharField(max_length=20, db_index=True)
    type = models.CharField(max_length=50)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["device_imei", "time"])]


class Trip(models.Model):
    """Résumé de trajet (alimenté par agrégat continu / worker)."""

    device_imei = models.CharField(max_length=20, db_index=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    distance_km = models.FloatField(default=0)
    duration_s = models.IntegerField(default=0)
    max_speed = models.FloatField(default=0)
    avg_speed = models.FloatField(default=0)
