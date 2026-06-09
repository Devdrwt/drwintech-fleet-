from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from .models import TraccarSyncLog


class TraccarSyncLogSerializer(ModelSerializer):
    class Meta:
        model = TraccarSyncLog
        fields = "__all__"


class TraccarSyncStatusView(generics.ListAPIView):
    """GET /integrations/traccar/status/ — derniers logs de sync."""

    serializer_class = TraccarSyncLogSerializer
    permission_classes = [IsAuthenticated]
    queryset = TraccarSyncLog.objects.order_by("-started_at")[:20]
