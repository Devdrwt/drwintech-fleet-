from rest_framework import serializers, viewsets
from rest_framework.routers import DefaultRouter

from apps.accounts.scoping import ClientScopedMixin

from .models import Charge, Invoice, Subscription, Transaction


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ["external_id", "raw_response", "paid_at", "status"]


class ChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = "__all__"
        read_only_fields = ["created_by"]


class SubscriptionViewSet(ClientScopedMixin, viewsets.ModelViewSet):
    client_filter = "client_id"
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class InvoiceViewSet(ClientScopedMixin, viewsets.ModelViewSet):
    client_filter = "client_id"
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class TransactionViewSet(ClientScopedMixin, viewsets.ModelViewSet):
    client_filter = "client_id"
    queryset = Transaction.objects.select_related("client").all()
    serializer_class = TransactionSerializer


class ChargeViewSet(viewsets.ModelViewSet):
    # Dépenses internes : réservées au back-office, jamais visibles d'un client.
    serializer_class = ChargeSerializer

    def get_queryset(self):
        if getattr(self.request.user, "client_id", None):
            return Charge.objects.none()
        return Charge.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


router = DefaultRouter()
router.register("billing/subscriptions", SubscriptionViewSet, basename="subscription")
router.register("billing/invoices", InvoiceViewSet, basename="invoice")
router.register("billing/transactions", TransactionViewSet, basename="transaction")
router.register("billing/charges", ChargeViewSet, basename="charge")

urlpatterns = router.urls
