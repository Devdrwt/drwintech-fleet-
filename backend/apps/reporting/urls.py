from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.crm.models import Client
from apps.fleet.models import GpsUnit


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """KPIs principaux du tableau de bord."""
    units = GpsUnit.objects.all()
    data = {
        "clients_actifs": Client.objects.filter(status="active").count(),
        "balises_total": units.count(),
        "balises_actives": units.filter(status="active").count(),
        "balises_suspendues": units.filter(status="suspended").count(),
        "balises_en_stock": units.filter(status="in_stock").count(),
        "balises_en_maintenance": units.filter(status="maintenance").count(),
    }
    # TODO Phase 4 : CA (mois/trimestre/année), alertes, évolution clients.
    return Response(data)


urlpatterns = [
    path("reporting/dashboard/", dashboard, name="dashboard"),
]
