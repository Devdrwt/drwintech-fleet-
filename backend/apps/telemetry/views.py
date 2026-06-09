from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Position, Trip
from .serializers import PositionSerializer, TripSerializer


def _client_imeis(user):
    """IMEI des balises du client de l'utilisateur (None = pas de restriction)."""
    client_id = getattr(user, "client_id", None)
    if not client_id:
        return None
    from apps.fleet.models import GpsUnit

    return list(
        GpsUnit.objects.filter(client_id=client_id).values_list("imei", flat=True)
    )


class PositionHistoryView(generics.ListAPIView):
    """GET /telemetry/positions/?imei=...&from=...&to=... — historique."""

    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Position.objects.all()
        imeis = _client_imeis(self.request.user)
        if imeis is not None:
            qs = qs.filter(device_imei__in=imeis)  # cloisonnement client
        imei = self.request.query_params.get("imei")
        if imei:
            qs = qs.filter(device_imei=imei)
        return qs.order_by("-time")[:1000]


class TripListView(generics.ListAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Trip.objects.all()
        imeis = _client_imeis(self.request.user)
        if imeis is not None:
            qs = qs.filter(device_imei__in=imeis)
        imei = self.request.query_params.get("imei")
        if imei:
            qs = qs.filter(device_imei=imei)
        return qs.order_by("-start_time")
