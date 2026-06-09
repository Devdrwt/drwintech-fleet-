from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

api_v1 = [
    path("", include("apps.accounts.urls")),
    path("", include("apps.crm.urls")),
    path("", include("apps.fleet.urls")),
    path("", include("apps.telemetry.urls")),
    path("", include("apps.geofencing.urls")),
    path("", include("apps.billing.urls")),
    path("", include("apps.maintenance.urls")),
    path("", include("apps.notifications.urls")),
    path("", include("apps.reporting.urls")),
    path("", include("apps.audit.urls")),
    path("", include("apps.integrations.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1, "api"), namespace="v1")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
