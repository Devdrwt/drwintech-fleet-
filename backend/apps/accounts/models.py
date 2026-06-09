from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """Rôle RBAC (voir SECURITY.md)."""

    class Level(models.IntegerChoices):
        USER = 1, "Utilisateur"
        SUPERVISOR = 2, "Superviseur"
        ADMIN = 3, "Admin"
        SUPERADMIN = 4, "Super Admin"

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    level = models.IntegerField(choices=Level.choices, default=Level.USER)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Utilisateur : login par email ou téléphone."""

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, null=True, blank=True, related_name="users"
    )
    # Lien optionnel vers un client (espace client). FK déclarée en string
    # pour éviter l'import croisé (frontière de module — voir ADR 0005).
    client = models.ForeignKey(
        "crm.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_accounts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def role_level(self) -> int:
        return self.role.level if self.role else 0
