from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import FleetTokenObtainPairSerializer, UserSerializer


class FleetTokenObtainPairView(TokenObtainPairView):
    """POST /auth/token/ — login email OU téléphone."""

    serializer_class = FleetTokenObtainPairSerializer


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /users/me/ — profil de l'utilisateur connecté."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
