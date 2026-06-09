from django.db import models


class NotificationTemplate(models.Model):
    code = models.CharField(max_length=80, unique=True)
    channel = models.CharField(max_length=10)  # email / sms / push
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    locale = models.CharField(max_length=5, default="fr")


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
