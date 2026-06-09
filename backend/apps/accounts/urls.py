from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CurrentUserView, FleetTokenObtainPairView

urlpatterns = [
    path("auth/token/", FleetTokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", CurrentUserView.as_view(), name="current_user"),
]
