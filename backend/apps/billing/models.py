from django.conf import settings
from django.db import models


class Subscription(models.Model):
    class Period(models.TextChoices):
        MONTHLY = "monthly", "Mensuel"
        QUARTERLY = "quarterly", "Trimestriel"
        ANNUAL = "annual", "Annuel"

    client = models.ForeignKey(
        "crm.Client", on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="XOF")
    period = models.CharField(
        max_length=12, choices=Period.choices, default=Period.MONTHLY
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    # Date de la prochaine facture à émettre (null = pas de facturation auto).
    next_invoice_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        ISSUED = "issued", "Émise"
        PAID = "paid", "Payée"
        OVERDUE = "overdue", "En retard"
        CANCELLED = "cancelled", "Annulée"

    client = models.ForeignKey(
        "crm.Client", on_delete=models.CASCADE, related_name="invoices"
    )
    number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="XOF")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    pdf_url = models.URLField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    class Provider(models.TextChoices):
        GOBIPAY = "gobipay", "Gobipay"
        FEDAPAY = "fedapay", "Fedapay"
        NOTCHPAY = "notchpay", "Notchpay"

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        SUCCESS = "success", "Réussi"
        FAILED = "failed", "Échoué"
        CANCELLED = "cancelled", "Annulé"

    client = models.ForeignKey(
        "crm.Client", on_delete=models.CASCADE, related_name="transactions"
    )
    invoice = models.ForeignKey(
        "billing.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    provider = models.CharField(max_length=20, choices=Provider.choices)
    external_id = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="XOF")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    payment_url = models.URLField(blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Charge(models.Model):
    """Dépenses internes (comptabilité)."""

    class Category(models.TextChoices):
        SIM_DATA = "sim_data", "Data SIM"
        REPAIRS = "repairs", "Réparations"
        TECHNICAL = "technical", "Technique"
        FIXED = "fixed", "Charges fixes"
        PURCHASE_BEACON = "purchase_beacon", "Achat boîtier"
        OTHER = "other", "Autre"

    category = models.CharField(max_length=20, choices=Category.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="XOF")
    description = models.CharField(max_length=255, blank=True)
    charge_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
