"""
Middleware d'audit : journalise les écritures (POST/PUT/PATCH/DELETE)
des utilisateurs authentifiés. Append-only (voir SECURITY.md).
"""
import json

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._maybe_log(request, response)
        except Exception:
            # L'audit ne doit jamais casser la requête.
            pass
        return response

    def _maybe_log(self, request, response):
        if request.method not in WRITE_METHODS:
            return
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return
        if not request.path.startswith("/api/"):
            return

        # Import différé pour éviter les soucis de chargement d'app.
        from .models import AuditLog

        changes = {}
        try:
            if request.body:
                changes = json.loads(request.body.decode("utf-8"))
                changes.pop("password", None)  # ne jamais journaliser de secret
        except Exception:
            changes = {}

        AuditLog.objects.create(
            user=user,
            user_email=getattr(user, "email", ""),
            action=request.method.lower(),
            resource_type=request.path,
            changes=changes,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        )
