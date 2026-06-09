from rest_framework import serializers, viewsets
from rest_framework.routers import DefaultRouter

from apps.accounts.scoping import ClientScopedMixin

from .models import Intervention


class InterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = "__all__"


class InterventionViewSet(ClientScopedMixin, viewsets.ModelViewSet):
    client_filter = "gps_unit__client_id"
    queryset = Intervention.objects.select_related("gps_unit").all()
    serializer_class = InterventionSerializer


router = DefaultRouter()
router.register("maintenance/interventions", InterventionViewSet, basename="intervention")

urlpatterns = router.urls
