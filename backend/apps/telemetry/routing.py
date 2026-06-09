from django.urls import path

from .consumers import AlertConsumer, LivePositionConsumer

websocket_urlpatterns = [
    path("ws/positions/", LivePositionConsumer.as_asgi()),
    path("ws/alerts/", AlertConsumer.as_asgi()),
]
