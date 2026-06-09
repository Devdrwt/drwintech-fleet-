from django.urls import path
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from apps.accounts.permissions import IsAdmin

from .models import AuditLog


class AuditLogSerializer(ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = AuditLog.objects.order_by("-created_at")


urlpatterns = [
    path("audit/logs/", AuditLogListView.as_view(), name="audit_logs"),
]
