from django.db import models


class NotificationTemplate(models.Model):
    code = models.CharField(max_length=80, unique=True)
    channel = models.CharField(max_length=10)  # email / sms / push
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    locale = models.CharField(max_length=5, default="fr")


class PushSubscription(models.Model):
    """Abonnement Web Push d'un utilisateur (un par appareil/navigateur)."""

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="push_subscriptions"
    )
    endpoint = models.URLField(max_length=600, unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def as_subscription_info(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }


class NotificationLog(models.Model):
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push"

    channel = models.CharField(max_length=10, choices=Channel.choices)
    recipient = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, blank=True)
    template_code = models.CharField(max_length=80, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
