from django.conf import settings
from django.db import models


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        CAR = "car", "Voiture"
        MOTO = "moto", "Moto"
        TRUCK = "truck", "Camion"
        MACHINE = "machine", "Engin"
        OTHER = "other", "Autre"

    client = models.ForeignKey(
        "crm.Client", on_delete=models.CASCADE, related_name="vehicles"
    )
    name = models.CharField(max_length=120)
    plate = models.CharField(max_length=30, blank=True)
    type = models.CharField(
        max_length=20, choices=VehicleType.choices, default=VehicleType.CAR
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.plate})"


class GpsUnit(models.Model):
    """Boîtier GPS. `imei` = identité partagée avec Traccar (uniqueId)."""

    class Status(models.TextChoices):
        IN_STOCK = "in_stock", "En stock"
        ACTIVE = "active", "Actif"
        SUSPENDED = "suspended", "Suspendu"
        MAINTENANCE = "maintenance", "En maintenance"
        TERMINATED = "terminated", "Résilié"
        INACTIVE = "inactive", "Inactif"

    vehicle = models.OneToOneField(
        Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="gps_unit"
    )
    client = models.ForeignKey(
        "crm.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gps_units",
    )
    imei = models.CharField(max_length=20, unique=True, db_index=True)
    traccar_device_id = models.IntegerField(null=True, blank=True)
    serial_number = models.CharField(max_length=80, blank=True)
    brand = models.CharField(max_length=60, blank=True)
    model_name = models.CharField(max_length=60, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.IN_STOCK
    )
    installed_at = models.DateField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.imei} ({self.brand} {self.model_name})"


class SimCard(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspendue"
        INACTIVE = "inactive", "Inactive"
        PENDING = "pending", "En attente"

    unit = models.OneToOneField(
        GpsUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name="sim_card"
    )
    iccid = models.CharField(max_length=25, unique=True)
    phone_number = models.CharField(max_length=30, blank=True)
    operator = models.CharField(max_length=60, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    data_credit_mb = models.IntegerField(default=0)
    activated_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.iccid


class SimRecharge(models.Model):
    sim_card = models.ForeignKey(
        SimCard, on_delete=models.CASCADE, related_name="recharges"
    )
    recharged_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="XOF")
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
