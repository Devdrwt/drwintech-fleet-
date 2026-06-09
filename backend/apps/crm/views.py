from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by("-created_at")
    serializer_class = ClientSerializer

    @action(detail=True, methods=["get"], url_path="360")
    def client_360(self, request, pk=None):
        """Vue 360° : profil + parc + paiements + interventions (agrégat)."""
        client = self.get_object()
        data = ClientSerializer(client).data
        # TODO Phase 3 : agréger units/transactions/interventions via services.
        data.update({
            "gps_units": [],
            "recent_transactions": [],
            "interventions": [],
            "events": [],
        })
        return Response(data)
