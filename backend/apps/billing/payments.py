"""
Abstraction des prestataires de paiement.

Mode `sandbox` : fonctionnel sans clé (génère une transaction en attente + une
URL de retour, le webhook confirme). Les prestataires réels (Gobipay, Fedapay,
Notchpay) héritent et surchargent `initiate`/`verify_webhook` une fois les clés
fournies. Sans clé configurée, ils retombent sur le comportement sandbox.
"""
import logging
import uuid

import httpx
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class BaseProvider:
    name = "sandbox"

    def authenticate_webhook(self, request) -> bool:
        """Authentifie l'appel webhook. Par défaut : accepté (le statut est de
        toute façon re-vérifié à la source). Surchargé par les prestataires."""
        return True

    def initiate(self, tx):
        """Crée la référence externe + l'URL de paiement. Retourne l'URL."""
        tx.external_id = f"{self.name.upper()}-{uuid.uuid4().hex[:12]}"
        base = settings.PAYMENT_RETURN_BASE.rstrip("/")
        tx.payment_url = f"{base}/client/paiement/retour?tx={tx.id}"
        tx.save(update_fields=["external_id", "payment_url"])
        return tx.payment_url

    def verify_webhook(self, data: dict):
        """Retourne (external_id, status normalisé) depuis le payload webhook.
        À surcharger avec la vérification de signature du prestataire réel."""
        status = (data.get("status") or "").lower()
        normalized = "success" if status in ("success", "successful", "paid") else "failed"
        return data.get("external_id"), normalized


class GobipayProvider(BaseProvider):
    name = "gobipay"
    # TODO : appel httpx réel + vérification de signature quand GOBIPAY_API_KEY fourni.


class FedapayProvider(BaseProvider):
    """Intégration FedaPay (Mobile Money). Repli sandbox interne si pas de clé."""

    name = "fedapay"

    def authenticate_webhook(self, request) -> bool:
        """Vérifie la signature HMAC FedaPay si un secret est configuré.
        Format attendu : header `x-fedapay-signature` = "t=<ts>,s=<hmac>" avec
        hmac = HMAC_SHA256(secret, f"{ts}.{raw_body}")."""
        secret = settings.FEDAPAY_WEBHOOK_SECRET
        if not secret:
            return True  # pas de secret -> on s'appuie sur la re-vérification API
        import hashlib
        import hmac as hmac_mod

        header = request.headers.get("X-FEDAPAY-SIGNATURE", "")
        parts = dict(
            p.split("=", 1) for p in header.split(",") if "=" in p
        )
        ts, sig = parts.get("t"), parts.get("s")
        if not ts or not sig:
            return False
        signed = f"{ts}.{request.body.decode('utf-8')}".encode()
        expected = hmac_mod.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        return hmac_mod.compare_digest(expected, sig)

    def _base_url(self) -> str:
        env_ = (settings.FEDAPAY_ENVIRONMENT or "sandbox").lower()
        return (
            "https://api.fedapay.com/v1"
            if env_ in ("live", "production")
            else "https://sandbox-api.fedapay.com/v1"
        )

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.FEDAPAY_SECRET_KEY}",
            "Content-Type": "application/json",
        }

    def initiate(self, tx):
        if not settings.FEDAPAY_SECRET_KEY:
            return super().initiate(tx)  # repli sandbox interne
        base = self._base_url()
        client = tx.client
        callback = f"{settings.PAYMENT_RETURN_BASE.rstrip('/')}/client/paiement/retour?tx={tx.id}"
        with httpx.Client(timeout=20) as http:
            # 1) Création de la transaction FedaPay
            r = http.post(
                f"{base}/transactions",
                headers=self._headers(),
                json={
                    "description": f"Facture {tx.invoice_id or ''}".strip(),
                    "amount": int(tx.amount),
                    "currency": {"iso": tx.currency or "XOF"},
                    "callback_url": callback,
                    "customer": {
                        "firstname": (client.name or "Client")[:50],
                        "email": client.email or f"client{client.id}@drwintech.com",
                    },
                },
            )
            r.raise_for_status()
            fedapay_id = r.json()["v1/transaction"]["id"]
            # 2) Génération du token + URL de paiement hébergée
            t = http.post(
                f"{base}/transactions/{fedapay_id}/token", headers=self._headers()
            )
            t.raise_for_status()
            url = t.json()["url"]
        tx.external_id = str(fedapay_id)
        tx.payment_url = url
        tx.save(update_fields=["external_id", "payment_url"])
        return url

    def verify_webhook(self, data: dict):
        # FedaPay : on ne fait pas confiance au payload, on re-vérifie le statut
        # réel via l'API (entity.id ou data.id selon le format reçu).
        entity = data.get("entity") or data.get("data") or data
        fedapay_id = entity.get("id") or data.get("external_id")
        if not fedapay_id or not settings.FEDAPAY_SECRET_KEY:
            return (str(fedapay_id) if fedapay_id else None), self._normalize(
                entity.get("status", "")
            )
        try:
            with httpx.Client(timeout=20) as http:
                r = http.get(
                    f"{self._base_url()}/transactions/{fedapay_id}",
                    headers=self._headers(),
                )
                r.raise_for_status()
                status = r.json()["v1/transaction"]["status"]
            return str(fedapay_id), self._normalize(status)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Vérif FedaPay échouée (%s) : %s", fedapay_id, exc)
            return str(fedapay_id), "failed"

    @staticmethod
    def _normalize(status: str) -> str:
        return "success" if str(status).lower() in ("approved", "success", "paid") else "failed"


class NotchpayProvider(BaseProvider):
    name = "notchpay"


_PROVIDERS = {
    "sandbox": BaseProvider(),
    "gobipay": GobipayProvider(),
    "fedapay": FedapayProvider(),
    "notchpay": NotchpayProvider(),
}


def get_provider(name: str) -> BaseProvider:
    return _PROVIDERS.get(name, _PROVIDERS["sandbox"])


def confirm_transaction(tx, status: str):
    """Applique le résultat d'un paiement : maj transaction, facture, encours."""
    from .models import Invoice

    if status == "success" and tx.status != "success":
        tx.status = "success"
        tx.paid_at = timezone.now()
        tx.save(update_fields=["status", "paid_at"])
        if tx.invoice_id:
            Invoice.objects.filter(id=tx.invoice_id).update(status=Invoice.Status.PAID)
        # Décrémente l'encours du client.
        client = tx.client
        client.outstanding_balance = max(0, client.outstanding_balance - tx.amount)
        client.save(update_fields=["outstanding_balance"])
    elif status != "success":
        tx.status = "failed"
        tx.save(update_fields=["status"])
    return tx
