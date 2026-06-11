from datetime import timedelta

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.crm.models import Client
from apps.fleet.models import GpsUnit
from apps.geofencing.models import AlertEvent

from . import services


def _alerts_count(client_id, days: int = 30) -> int:
    since = timezone.now() - timedelta(days=days)
    qs = AlertEvent.objects.filter(triggered_at__gte=since)
    if client_id:
        imeis = GpsUnit.objects.filter(client_id=client_id).values_list("imei", flat=True)
        qs = qs.filter(device_imei__in=list(imeis))
    return qs.count()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """KPIs principaux du tableau de bord (cloisonnés si utilisateur client)."""
    client_id = getattr(request.user, "client_id", None)
    today = timezone.localdate()

    units = GpsUnit.objects.all()
    clients = Client.objects.all()
    if client_id:
        units = units.filter(client_id=client_id)
        clients = clients.filter(id=client_id)

    end = today + timedelta(days=1)  # borne haute inclusive sur aujourd'hui
    unpaid = services.unpaid_summary(client_id)

    data = {
        # Parc
        "balises_total": units.count(),
        "balises_actives": units.filter(status="active").count(),
        "balises_suspendues": units.filter(status="suspended").count(),
        "balises_en_stock": units.filter(status="in_stock").count(),
        "balises_en_maintenance": units.filter(status="maintenance").count(),
        # Clients
        "clients_total": clients.count(),
        "clients_actifs": clients.filter(status="active").count(),
        "clients_nouveaux_30j": services.new_clients(30, client_id),
        # Chiffre d'affaires encaissé
        "ca_mois": services.revenue_between(today.replace(day=1), end, client_id),
        "ca_trimestre": services.revenue_between(
            services.quarter_start(today), end, client_id
        ),
        "ca_annee": services.revenue_between(today.replace(month=1, day=1), end, client_id),
        # Impayés
        "impayes_count": unpaid["count"],
        "impayes_total": unpaid["total"],
        # Alertes
        "alertes_30j": _alerts_count(client_id, 30),
    }
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def revenue(request):
    """Série du CA encaissé par mois (par défaut 12 mois) pour les graphiques."""
    client_id = getattr(request.user, "client_id", None)
    try:
        months = min(max(int(request.query_params.get("months", 12)), 1), 36)
    except (TypeError, ValueError):
        months = 12
    return Response({"months": months, "series": services.monthly_revenue(months, client_id)})
