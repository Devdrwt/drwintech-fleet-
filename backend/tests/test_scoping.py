import pytest


@pytest.mark.django_db
def test_client_sees_only_own_units(api, user_a, unit_a, unit_b):
    api.force_authenticate(user=user_a)
    res = api.get("/api/v1/fleet/units/").json()
    imeis = [u["imei"] for u in res["results"]]
    assert imeis == ["IMEIA0000000000001"]


@pytest.mark.django_db
def test_client_sees_only_own_client_record(api, user_a, client_a, client_b):
    api.force_authenticate(user=user_a)
    res = api.get("/api/v1/clients/").json()
    names = [c["name"] for c in res["results"]]
    assert names == ["Client A"]


@pytest.mark.django_db
def test_backoffice_sees_all_units(api, admin_user, unit_a, unit_b):
    api.force_authenticate(user=admin_user)
    res = api.get("/api/v1/fleet/units/").json()
    assert res["count"] == 2


@pytest.mark.django_db
def test_unauthenticated_is_rejected(api, unit_a):
    assert api.get("/api/v1/fleet/units/").status_code == 401
