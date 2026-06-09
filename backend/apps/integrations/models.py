from django.db import models


class TraccarSyncLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Succès"
        PARTIAL = "partial", "Partiel"
        FAILED = "failed", "Échec"

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices)
    devices_synced = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
