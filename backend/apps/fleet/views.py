from rest_framework import viewsets

from .models import GpsUnit, SimCard, SimRecharge, Vehicle
from .serializers import (
    GpsUnitSerializer,
    SimCardSerializer,
    SimRechargeSerializer,
    VehicleSerializer,
)
from .services import deprovision_unit_on_traccar, provision_unit_on_traccar


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related("client").all()
    serializer_class = VehicleSerializer


class GpsUnitViewSet(viewsets.ModelViewSet):
    queryset = GpsUnit.objects.select_related("client", "vehicle").all()
    serializer_class = GpsUnitSerializer

    def perform_create(self, serializer):
        """À la création, provisionne le device sur le moteur Traccar."""
        unit = serializer.save()
        provision_unit_on_traccar(unit)

    def perform_destroy(self, instance):
        """Supprime aussi le device côté moteur (best-effort)."""
        deprovision_unit_on_traccar(instance)
        instance.delete()


class SimCardViewSet(viewsets.ModelViewSet):
    queryset = SimCard.objects.select_related("unit").all()
    serializer_class = SimCardSerializer


class SimRechargeViewSet(viewsets.ModelViewSet):
    queryset = SimRecharge.objects.select_related("sim_card").all()
    serializer_class = SimRechargeSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
