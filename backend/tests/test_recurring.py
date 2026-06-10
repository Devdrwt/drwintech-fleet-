import datetime
from decimal import Decimal

import pytest

from apps.billing.models import Invoice, Subscription
from apps.billing.tasks import (
    add_period,
    generate_due_invoices,
    mark_overdue_invoices,
    send_invoice_reminders,
)
from apps.crm.models import Client


def test_add_period_month_overflow():
    # 31 janvier + 1 mois -> 28 février (année non bissextile)
    assert add_period(datetime.date(2026, 1, 31), "monthly") == datetime.date(2026, 2, 28)
    assert add_period(datetime.date(2026, 1, 15), "quarterly") == datetime.date(2026, 4, 15)
    assert add_period(datetime.date(2026, 6, 10), "annual") == datetime.date(2027, 6, 10)


@pytest.mark.django_db
def test_generate_due_invoice_advances_and_bills():
    today = datetime.date(2026, 6, 10)
    client = Client.objects.create(name="Recurr", outstanding_balance=Decimal("0"))
    sub = Subscription.objects.create(
        client=client,
        plan="GPS Mensuel",
        amount=Decimal("50000"),
        currency="XOF",
        period="monthly",
        start_date=today,
        next_invoice_date=today,
        is_active=True,
    )
    created = generate_due_invoices(today=today)
    assert created == 1

    inv = Invoice.objects.get(client=client)
    assert inv.status == "issued"
    assert inv.due_date == today + datetime.timedelta(days=7)
    client.refresh_from_db()
    sub.refresh_from_db()
    assert client.outstanding_balance == Decimal("50000")
    assert sub.next_invoice_date == datetime.date(2026, 7, 10)

    # Idempotence : relancer le même jour ne recrée pas de facture.
    assert generate_due_invoices(today=today) == 0
    assert Invoice.objects.filter(client=client).count() == 1


@pytest.mark.django_db
def test_mark_overdue_invoices():
    today = datetime.date(2026, 6, 10)
    client = Client.objects.create(name="Late")
    Invoice.objects.create(
        client=client,
        number="FA-LATE-1",
        amount=Decimal("1000"),
        status="issued",
        due_date=today - datetime.timedelta(days=1),
    )
    assert mark_overdue_invoices(today=today) == 1
    assert Invoice.objects.get(number="FA-LATE-1").status == "overdue"


@pytest.mark.django_db
def test_send_invoice_reminders():
    today = datetime.date(2026, 6, 10)
    client = Client.objects.create(name="Remind", email="r@test.com")
    Invoice.objects.create(
        client=client, number="FA-REM-1", amount=Decimal("1000"),
        status="issued", due_date=today,  # échéance aujourd'hui -> rappel
    )
    sent = send_invoice_reminders(today=today)
    assert sent == 1
