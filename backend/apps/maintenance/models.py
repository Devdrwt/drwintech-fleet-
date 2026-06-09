from django.db import models


class Intervention(models.Model):
    class Type(models.TextChoices):
        PREVENTIVE = "preventive", "Préventive"
        CORRECTIVE = "corrective", "Corrective"
        REPLACEMENT = "replacement", "Remplacement"

    class Status(models.TextChoices):
        OPEN = "open", "Ouverte"
        IN_PROGRESS = "in_progress", "En cours"
        COMPLETED = "completed", "Terminée"
        CANCELLED = "cancelled", "Annulée"

    gps_unit = models.ForeignKey(
        "fleet.GpsUnit", on_delete=models.CASCADE, related_name="interventions"
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
