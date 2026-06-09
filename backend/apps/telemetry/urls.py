from django.urls import path

from .views import PositionHistoryView, TripListView

urlpatterns = [
    path("telemetry/positions/", PositionHistoryView.as_view(), name="positions"),
    path("telemetry/trips/", TripListView.as_view(), name="trips"),
]
