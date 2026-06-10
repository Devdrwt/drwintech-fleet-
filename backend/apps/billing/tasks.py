"""
Facturation récurrente (Celery beat) :
- génération automatique des factures dues à partir des abonnements actifs,
- passage des factures échues en `overdue`,
- rappels (push + journal) à J-7, J-3, J et en retard,
- suspension des clients en retard au-delà du délai de grâce.
"""
import calendar
import datetime
from decimal import Decimal

from celery import shared_task
from django.conf import settings
from django.utils import timezone


def add_period(d: datetime.date, period: str) -> datetime.date:
    months = {"monthly": 1, "quarterly": 3, "annual": 12}.get(period, 1)
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


@shared_task
def generate_due_invoices(today=None) -> int:
    """Émet les factures des abonnements dont next_invoice_date <= aujourd'hui."""
    from .models import Invoice, Subscription

    today = today or timezone.localdate()
    grace = settings.PAYMENT_GRACE_DAYS
    created = 0
    subs = Subscription.objects.filter(
        is_active=True, next_invoice_date__isnull=False, next_invoice_date__lte=today
    ).select_related("client")
    for sub in subs:
        due = sub.next_invoice_date
        number = f"FA-{sub.id}-{due:%Y%m%d}"
        if Invoice.objects.filter(number=number).exists():
            sub.next_invoice_date = add_period(due, sub.period)
            sub.save(update_fields=["next_invoice_date"])
            continue
        Invoice.objects.create(
            client=sub.client,
            number=number,
            amount=sub.amount,
            currency=sub.currency,
            status=Invoice.Status.ISSUED,
            due_date=due + datetime.timedelta(days=grace),
        )
        client = sub.client
        client.outstanding_balance = (client.outstanding_balance or Decimal("0")) + sub.amount
        client.save(update_fields=["outstanding_balance"])
        sub.next_invoice_date = add_period(due, sub.period)
        sub.save(update_fields=["next_invoice_date"])
        created += 1
    return created


@shared_task
def mark_overdue_invoices(today=None) -> int:
    """Passe en `overdue` les factures émises dont l'échéance est dépassée."""
    from .models import Invoice

    today = today or timezone.localdate()
    return Invoice.objects.filter(
        status=Invoice.Status.ISSUED, due_date__lt=today
    ).update(status=Invoice.Status.OVERDUE)


@shared_task
def send_invoice_reminders(today=None) -> int:
    """Rappels à J-7 / J-3 / J / en retard pour les factures non payées."""
    from apps.notifications.models import NotificationLog
    from apps.notifications.push import send_to_client

    from .models import Invoice

    today = today or timezone.localdate()
    targets = {today + datetime.timedelta(days=7), today + datetime.timedelta(days=3), today}
    sent = 0
    invoices = Invoice.objects.filter(
        status__in=[Invoice.Status.ISSUED, Invoice.Status.OVERDUE],
        due_date__isnull=False,
    ).select_related("client")
    for inv in invoices:
        overdue = inv.due_date < today
        if not overdue and inv.due_date not in targets:
            continue
        subject = "Facture en retard" if overdue else f"Facture à régler (éch. {inv.due_date})"
        body = f"Facture {inv.number} : {inv.amount} {inv.currency}"
        NotificationLog.objects.create(
            channel="push",
            recipient=inv.client.email or inv.client.name,
            subject=subject,
            template_code="invoice_reminder",
            success=True,
        )
        try:
            send_to_client(inv.client_id, subject, body, {"url": "/client/factures"})
        except Exception:  # noqa: BLE001 — le rappel ne doit pas échouer la tâche
            pass
        sent += 1
    return sent


@shared_task
def suspend_overdue_clients(today=None) -> int:
    """Suspend les clients dont une facture est en retard au-delà du délai de grâce."""
    from apps.crm.models import Client

    from .models import Invoice

    today = today or timezone.localdate()
    limit = today - datetime.timedelta(days=settings.PAYMENT_GRACE_DAYS)
    client_ids = (
        Invoice.objects.filter(status=Invoice.Status.OVERDUE, due_date__lt=limit)
        .values_list("client_id", flat=True)
        .distinct()
    )
    return Client.objects.filter(
        id__in=list(client_ids), status=Client.Status.ACTIVE
    ).update(status=Client.Status.SUSPENDED)
