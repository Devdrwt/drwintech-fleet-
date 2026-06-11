from django.urls import path

from .views import dashboard, revenue

urlpatterns = [
    path("reporting/dashboard/", dashboard, name="dashboard"),
    path("reporting/revenue/", revenue, name="revenue"),
]
