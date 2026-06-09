from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Position, Trip
from .serializers import PositionSerializer, TripSerializer


class PositionHistoryView(generics.ListAPIView):
    """GET /telemetry/positions/?imei=...&from=...&to=... — historique."""

    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Position.objects.all()
        imei = self.request.query_params.get("imei")
        if imei:
            qs = qs.filter(device_imei=imei)
        return qs.order_by("-time")[:1000]


class TripListView(generics.ListAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Trip.objects.all()
        imei = self.request.query_params.get("imei")
        if imei:
            qs = qs.filter(device_imei=imei)
        return qs.order_by("-start_time")
