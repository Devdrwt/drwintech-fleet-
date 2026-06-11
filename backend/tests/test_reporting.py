from decimal import Decimal

import pytest
from django.utils import timezone

from apps.billing.models import Invoice, Transaction
from apps.fleet.models import GpsUnit


def _success_tx(client, amount, when=None):
    return Transaction.objects.create(
        client=client,
        provider=Transaction.Provider.FEDAPAY,
        amount=Decimal(amount),
        status=Transaction.Status.SUCCESS,
        paid_at=when or timezone.now(),
    )


@pytest.mark.django_db
def test_dashboard_requires_auth(api):
    assert api.get("/api/v1/reporting/dashboard/").status_code == 401


@pytest.mark.django_db
def test_backoffice_dashboard_aggregates_all(api, admin_user, client_a, client_b):
    GpsUnit.objects.create(imei="IMEIA0000000000001", client=client_a, status="active")
    GpsUnit.objects.create(imei="IMEIB0000000000001", client=client_b, status="suspended")
    _success_tx(client_a, "5000")
    _success_tx(client_b, "3000")
    Invoice.objects.create(
        client=client_a, number="INV-OD-1", amount=Decimal("2000"),
        status=Invoice.Status.OVERDUE,
    )

    api.force_authenticate(user=admin_user)
    data = api.get("/api/v1/reporting/dashboard/").json()

    assert data["balises_total"] == 2
    assert data["balises_actives"] == 1
    assert data["balises_suspendues"] == 1
    assert data["clients_total"] == 2
    assert float(data["ca_mois"]) == 8000.0          # 5000 + 3000, ce mois-ci
    assert float(data["ca_annee"]) == 8000.0
    assert data["impayes_count"] == 1
    assert float(data["impayes_total"]) == 2000.0


@pytest.mark.django_db
def test_client_dashboard_is_scoped(api, user_a, client_a, client_b):
    GpsUnit.objects.create(imei="IMEIA0000000000001", client=client_a, status="active")
    GpsUnit.objects.create(imei="IMEIB0000000000001", client=client_b, status="active")
    _success_tx(client_a, "5000")
    _success_tx(client_b, "3000")

    api.force_authenticate(user=user_a)
    data = api.get("/api/v1/reporting/dashboard/").json()

    assert data["balises_total"] == 1               # seulement ses balises
    assert data["clients_total"] == 1
    assert float(data["ca_mois"]) == 5000.0          # seulement son CA
    assert data["clients_nouveaux_30j"] == 0         # masqué pour un client


@pytest.mark.django_db
def test_revenue_series_length_and_total(api, admin_user, client_a):
    _success_tx(client_a, "1500")  # ce mois-ci

    api.force_authenticate(user=admin_user)
    data = api.get("/api/v1/reporting/revenue/?months=6").json()

    assert data["months"] == 6
    assert len(data["series"]) == 6
    # Le dernier point (mois courant) porte le CA ; les précédents sont à 0.
    assert float(data["series"][-1]["total"]) == 1500.0
    assert all(float(p["total"]) == 0.0 for p in data["series"][:-1])
