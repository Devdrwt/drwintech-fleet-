from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.crm.models import Client
from apps.fleet.models import GpsUnit


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def role_client(db):
    role, _ = Role.objects.get_or_create(
        code="client", defaults={"name": "Client", "level": 1}
    )
    return role


@pytest.fixture
def client_a(db):
    return Client.objects.create(name="Client A", outstanding_balance=Decimal("100000"))


@pytest.fixture
def client_b(db):
    return Client.objects.create(name="Client B")


@pytest.fixture
def unit_a(client_a):
    return GpsUnit.objects.create(imei="IMEIA0000000000001", client=client_a)


@pytest.fixture
def unit_b(client_b):
    return GpsUnit.objects.create(imei="IMEIB0000000000001", client=client_b)


@pytest.fixture
def user_a(client_a, role_client):
    return User.objects.create_user(
        username="ua", email="ua@test.com", password="x", client=client_a, role=role_client
    )


@pytest.fixture
def admin_user(db):
    # Sans client => accès back-office (voit tout).
    return User.objects.create_user(username="adm", email="adm@test.com", password="x")
