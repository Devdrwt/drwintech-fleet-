from rest_framework import serializers, viewsets
from rest_framework.routers import DefaultRouter

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


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related("client").all()
    serializer_class = TransactionSerializer
    # TODO Phase 3 : initier le paiement auprès de l'agrégateur + webhook.


class ChargeViewSet(viewsets.ModelViewSet):
    queryset = Charge.objects.all()
    serializer_class = ChargeSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


router = DefaultRouter()
router.register("billing/subscriptions", SubscriptionViewSet, basename="subscription")
router.register("billing/invoices", InvoiceViewSet, basename="invoice")
router.register("billing/transactions", TransactionViewSet, basename="transaction")
router.register("billing/charges", ChargeViewSet, basename="charge")

urlpatterns = router.urls
