"""
Middleware d'authentification WebSocket par JWT (query string ?token=).
Remplace l'auth par session pour les connexions temps réel (voir SECURITY.md).
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def _get_user(user_id):
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Lit ?token=<access> sur le WebSocket, valide et place scope['user']."""

    async def __call__(self, scope, receive, send):
        from rest_framework_simplejwt.exceptions import TokenError
        from rest_framework_simplejwt.tokens import AccessToken

        query = parse_qs((scope.get("query_string") or b"").decode())
        token = (query.get("token") or [None])[0]
        scope["user"] = AnonymousUser()
        if token:
            try:
                access = AccessToken(token)
                scope["user"] = await _get_user(access["user_id"])
            except TokenError:
                pass
        return await super().__call__(scope, receive, send)
