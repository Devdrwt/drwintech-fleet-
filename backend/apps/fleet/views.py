from rest_framework import viewsets

from .models import GpsUnit, SimCard, SimRecharge, Vehicle
from .serializers import (
    GpsUnitSerializer,
    SimCardSerializer,
    SimRechargeSerializer,
    VehicleSerializer,
)


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related("client").all()
    serializer_class = VehicleSerializer


class GpsUnitViewSet(viewsets.ModelViewSet):
    queryset = GpsUnit.objects.select_related("client", "vehicle").all()
    serializer_class = GpsUnitSerializer

    # TODO Phase 2 : à la création, appeler integrations.traccar pour créer le
    # device correspondant (uniqueId = imei) et stocker traccar_device_id.


class SimCardViewSet(viewsets.ModelViewSet):
    queryset = SimCard.objects.select_related("unit").all()
    serializer_class = SimCardSerializer


class SimRechargeViewSet(viewsets.ModelViewSet):
    queryset = SimRecharge.objects.select_related("sim_card").all()
    serializer_class = SimRechargeSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
