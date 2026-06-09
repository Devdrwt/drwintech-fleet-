from rest_framework import serializers, viewsets
from rest_framework.routers import DefaultRouter

from .models import AlertRule, Geofence


class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = "__all__"


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = "__all__"


class GeofenceViewSet(viewsets.ModelViewSet):
    queryset = Geofence.objects.all()
    serializer_class = GeofenceSerializer


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer


router = DefaultRouter()
router.register("geofencing/geofences", GeofenceViewSet, basename="geofence")
router.register("geofencing/rules", AlertRuleViewSet, basename="alertrule")

urlpatterns = router.urls
