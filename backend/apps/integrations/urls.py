from django.urls import path

from .views import TraccarSyncStatusView

urlpatterns = [
    path(
        "integrations/traccar/status/",
        TraccarSyncStatusView.as_view(),
        name="traccar_status",
    ),
]
