from django.db import models


class Client(models.Model):
    class Type(models.TextChoices):
        INDIVIDUAL = "individual", "Particulier"
        COMPANY = "company", "Entreprise"

    class Status(models.TextChoices):
        ACTIVE = "active", "Actif"
        SUSPENDED = "suspended", "Suspendu"
        INACTIVE = "inactive", "Inactif"
        TERMINATED = "terminated", "Résilié"

    name = models.CharField(max_length=200)
    client_type = models.CharField(
        max_length=20, choices=Type.choices, default=Type.INDIVIDUAL
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    outstanding_balance = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )
    subscription_end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Contact(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="contacts"
    )
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
