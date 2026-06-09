"""
Envoi de notifications Web Push (VAPID) — voir SECURITY.md / Phase C.
"""
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def _vapid_private_key() -> str | None:
    try:
        with open(settings.VAPID_PRIVATE_KEY_PATH, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def send_to_client(client_id: int, title: str, body: str, data: dict | None = None):
    """Envoie une notif push à tous les abonnements des users du client donné."""
    from pywebpush import WebPushException, webpush

    from .models import NotificationLog, PushSubscription

    private_key = _vapid_private_key()
    if not private_key:
        logger.warning("VAPID privé introuvable : push ignoré.")
        return 0

    subs = PushSubscription.objects.filter(user__client_id=client_id)
    payload = json.dumps({"title": title, "body": body, **(data or {})})
    sent = 0
    for sub in subs:
        try:
            webpush(
                subscription_info=sub.as_subscription_info(),
                data=payload,
                vapid_private_key=private_key,
                vapid_claims={"sub": f"mailto:{settings.VAPID_CONTACT_EMAIL}"},
            )
            sent += 1
            NotificationLog.objects.create(
                channel="push", recipient=sub.endpoint[:200], subject=title, success=True
            )
        except WebPushException as exc:
            logger.warning("Push échoué (%s) : %s", sub.endpoint[:40], exc)
            NotificationLog.objects.create(
                channel="push",
                recipient=sub.endpoint[:200],
                subject=title,
                success=False,
                error_message=str(exc)[:500],
            )
            # 404/410 = abonnement expiré -> on le supprime.
            if exc.response is not None and exc.response.status_code in (404, 410):
                sub.delete()
    return sent
