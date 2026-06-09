from django.conf import settings
from django.urls import path
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NotificationLog, PushSubscription


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = "__all__"


class NotificationLogListView(generics.ListAPIView):
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]
    queryset = NotificationLog.objects.order_by("-sent_at")


class VapidPublicKeyView(APIView):
    """GET /push/vapid-public-key/ — clé publique pour s'abonner côté navigateur."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"public_key": settings.VAPID_PUBLIC_KEY})


class PushSubscribeView(APIView):
    """POST /push/subscribe/ — enregistre l'abonnement Web Push de l'utilisateur."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        endpoint = request.data.get("endpoint")
        keys = request.data.get("keys", {})
        if not endpoint or not keys.get("p256dh") or not keys.get("auth"):
            return Response({"detail": "Abonnement invalide."}, status=400)
        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                "user": request.user,
                "p256dh": keys["p256dh"],
                "auth": keys["auth"],
            },
        )
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)


urlpatterns = [
    path("notifications/logs/", NotificationLogListView.as_view(), name="notif_logs"),
    path("push/vapid-public-key/", VapidPublicKeyView.as_view(), name="vapid_key"),
    path("push/subscribe/", PushSubscribeView.as_view(), name="push_subscribe"),
]
