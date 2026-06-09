from django.urls import path

from .consumers import LivePositionConsumer

websocket_urlpatterns = [
    path("ws/positions/", LivePositionConsumer.as_asgi()),
]
