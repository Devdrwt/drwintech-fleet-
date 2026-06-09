from django.urls import path
from rest_framework import generics, serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter

from .models import AlertEvent, AlertRule, Geofence


class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = "__all__"


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = "__all__"


class AlertEventSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="rule.type", read_only=True)

    class Meta:
        model = AlertEvent
        fields = ["id", "type", "device_imei", "payload", "triggered_at", "notified"]


class AlertEventListView(generics.ListAPIView):
    """Liste des alertes, cloisonnée par client (par IMEI)."""

    serializer_class = AlertEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = AlertEvent.objects.select_related("rule").order_by("-triggered_at")
        client_id = getattr(self.request.user, "client_id", None)
        if client_id:
            from apps.fleet.models import GpsUnit

            imeis = list(
                GpsUnit.objects.filter(client_id=client_id).values_list("imei", flat=True)
            )
            qs = qs.filter(device_imei__in=imeis)
        return qs


class GeofenceViewSet(viewsets.ModelViewSet):
    queryset = Geofence.objects.all()
    serializer_class = GeofenceSerializer


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer


router = DefaultRouter()
router.register("geofencing/geofences", GeofenceViewSet, basename="geofence")
router.register("geofencing/rules", AlertRuleViewSet, basename="alertrule")

urlpatterns = router.urls + [
    path("geofencing/alerts/", AlertEventListView.as_view(), name="alert_events"),
]
