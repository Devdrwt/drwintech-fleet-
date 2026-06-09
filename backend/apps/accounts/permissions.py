from rest_framework.permissions import BasePermission


class HasRoleLevel(BasePermission):
    """Autorise si le niveau de rôle de l'utilisateur >= `min_level` sur la vue."""

    def has_permission(self, request, view):
        min_level = getattr(view, "min_role_level", 1)
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role_level >= min_level
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role_level >= 3
        )
