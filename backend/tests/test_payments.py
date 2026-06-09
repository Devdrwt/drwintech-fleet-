from decimal import Decimal

import pytest

from apps.billing.models import Invoice, Transaction


@pytest.fixture
def invoice_a(client_a):
    return Invoice.objects.create(
        client=client_a,
        number="FA-TEST-1",
        amount=Decimal("100000"),
        currency="XOF",
        status="issued",
    )


@pytest.mark.django_db
def test_pay_creates_pending_transaction(api, user_a, invoice_a):
    api.force_authenticate(user=user_a)
    res = api.post(
        "/api/v1/billing/pay/",
        {"invoice": invoice_a.id, "provider": "sandbox"},
        format="json",
    )
    assert res.status_code == 201
    body = res.json()
    tx = Transaction.objects.get(id=body["transaction_id"])
    assert tx.status == "pending"
    assert tx.invoice_id == invoice_a.id
    assert body["payment_url"]


@pytest.mark.django_db
def test_owner_can_download_invoice_pdf(api, user_a, invoice_a):
    api.force_authenticate(user=user_a)
    res = api.get(f"/api/v1/billing/invoices/{invoice_a.id}/pdf/")
    assert res.status_code == 200
    assert res["Content-Type"] == "application/pdf"
    assert res.content[:4] == b"%PDF"


@pytest.mark.django_db
def test_cannot_download_other_client_pdf(api, user_a, client_b):
    other = Invoice.objects.create(
        client=client_b, number="FA-B-PDF", amount=Decimal("1000"), status="issued"
    )
    api.force_authenticate(user=user_a)
    res = api.get(f"/api/v1/billing/invoices/{other.id}/pdf/")
    assert res.status_code == 403


@pytest.mark.django_db
def test_cannot_pay_other_client_invoice(api, user_a, client_b):
    other = Invoice.objects.create(
        client=client_b, number="FA-B-1", amount=Decimal("1000"), status="issued"
    )
    api.force_authenticate(user=user_a)
    res = api.post(
        "/api/v1/billing/pay/", {"invoice": other.id, "provider": "sandbox"}, format="json"
    )
    assert res.status_code == 403


@pytest.mark.django_db
def test_webhook_confirms_payment_and_decrements_balance(api, user_a, client_a, invoice_a):
    api.force_authenticate(user=user_a)
    pay = api.post(
        "/api/v1/billing/pay/",
        {"invoice": invoice_a.id, "provider": "sandbox"},
        format="json",
    ).json()
    tx = Transaction.objects.get(id=pay["transaction_id"])

    # Webhook public (sans auth)
    api.force_authenticate(user=None)
    res = api.post(
        "/api/v1/billing/webhook/sandbox/",
        {"external_id": tx.external_id, "status": "success"},
        format="json",
    )
    assert res.status_code == 200

    tx.refresh_from_db()
    invoice_a.refresh_from_db()
    client_a.refresh_from_db()
    assert tx.status == "success"
    assert invoice_a.status == "paid"
    assert client_a.outstanding_balance == Decimal("0")
