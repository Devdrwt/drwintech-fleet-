from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "name", "level"]


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_code = serializers.CharField(source="role.code", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name",
            "phone", "role", "role_code", "client",
        ]
        read_only_fields = ["id", "role", "client"]


class FleetTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login flexible : `email` peut contenir un email OU un téléphone.
    """

    username_field = "email"

    def validate(self, attrs):
        identifier = attrs.get("email", "")
        if identifier and "@" not in identifier:
            # Résout le téléphone vers l'email pour SimpleJWT.
            try:
                user = User.objects.get(phone=identifier)
                attrs["email"] = user.email
            except User.DoesNotExist:
                pass
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
