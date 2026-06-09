from django.urls import path
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated

from .models import NotificationLog


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = "__all__"


class NotificationLogListView(generics.ListAPIView):
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]
    queryset = NotificationLog.objects.order_by("-sent_at")


urlpatterns = [
    path("notifications/logs/", NotificationLogListView.as_view(), name="notif_logs"),
]
