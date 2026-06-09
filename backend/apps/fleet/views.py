from rest_framework import viewsets

from apps.accounts.scoping import ClientScopedMixin

from .models import GpsUnit, SimCard, SimRecharge, Vehicle
from .serializers import (
    GpsUnitSerializer,
    SimCardSerializer,
    SimRechargeSerializer,
    VehicleSerializer,
)
from .services import deprovision_unit_on_traccar, provision_unit_on_traccar


class VehicleViewSet(ClientScopedMixin, viewsets.ModelViewSet):
    client_filter = "client_id"
    queryset = Vehicle.objects.select_related("client").order_by("-created_at")
    serializer_class = VehicleSerializer


class GpsUnitViewSet(ClientScopedMixin, viewsets.ModelViewSet):
    client_filter = "client_id"
    queryset = GpsUnit.objects.select_related("client", "vehicle").order_by("-created_at")
    serializer_class = GpsUnitSerializer

    def perform_create(self, serializer):
        """À la création, provisionne le device sur le moteur Traccar."""
        unit = serializer.save()
        provision_unit_on_traccar(unit)

    def perform_destroy(self, instance):
        """Supprime aussi le device côté moteur (best-effort)."""
        deprovision_unit_on_traccar(instance)
        instance.delete()


class SimCardViewSet(ClientScopedMixin, viewsets.ModelViewSet):
    client_filter = "unit__client_id"
    queryset = SimCard.objects.select_related("unit").all()
    serializer_class = SimCardSerializer


class SimRechargeViewSet(ClientScopedMixin, viewsets.ModelViewSet):
    client_filter = "sim_card__unit__client_id"
    queryset = SimRecharge.objects.select_related("sim_card").all()
    serializer_class = SimRechargeSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
