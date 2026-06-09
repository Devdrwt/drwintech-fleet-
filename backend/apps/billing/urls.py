from django.http import HttpResponse
from django.urls import path
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView

from apps.accounts.scoping import ClientScopedMixin

from .models import Charge, Invoice, Subscription, Transaction
from .payments import confirm_transaction, get_provider
from .pdf import render_invoice_pdf


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


class InvoicePdfView(APIView):
    """GET /billing/invoices/<id>/pdf/ — PDF de la facture (cloisonné client)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        invoice = Invoice.objects.filter(id=pk).first()
        if not invoice:
            return Response({"detail": "Facture introuvable."}, status=404)
        client_id = getattr(request.user, "client_id", None)
        if client_id and invoice.client_id != client_id:
            return Response({"detail": "Accès refusé."}, status=403)
        pdf = render_invoice_pdf(invoice)
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f'inline; filename="facture-{invoice.number}.pdf"'
        return resp


class PayView(APIView):
    """POST /billing/pay/ — initie un paiement pour une facture du client."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        invoice_id = request.data.get("invoice")
        provider_name = request.data.get("provider", "sandbox")
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            return Response({"detail": "Facture introuvable."}, status=404)
        # Cloisonnement : un client ne paie que ses propres factures.
        client_id = getattr(request.user, "client_id", None)
        if client_id and invoice.client_id != client_id:
            return Response({"detail": "Accès refusé."}, status=403)

        tx = Transaction.objects.create(
            client=invoice.client,
            invoice=invoice,
            provider=provider_name,
            amount=invoice.amount,
            currency=invoice.currency,
            status=Transaction.Status.PENDING,
        )
        payment_url = get_provider(provider_name).initiate(tx)
        return Response(
            {"transaction_id": tx.id, "payment_url": payment_url, "status": tx.status},
            status=status.HTTP_201_CREATED,
        )


class PaymentWebhookView(APIView):
    """POST /billing/webhook/<provider>/ — callback agrégateur (public)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, provider):
        prov = get_provider(provider)
        if not prov.authenticate_webhook(request):
            return Response({"detail": "Signature invalide."}, status=403)
        external_id, result = prov.verify_webhook(request.data)
        if not external_id:
            return Response({"detail": "Payload invalide."}, status=400)
        tx = Transaction.objects.filter(external_id=external_id).first()
        if not tx:
            return Response({"detail": "Transaction inconnue."}, status=404)
        tx.raw_response = dict(request.data)
        tx.save(update_fields=["raw_response"])
        confirm_transaction(tx, result)
        return Response({"status": tx.status})


router = DefaultRouter()
router.register("billing/subscriptions", SubscriptionViewSet, basename="subscription")
router.register("billing/invoices", InvoiceViewSet, basename="invoice")
router.register("billing/transactions", TransactionViewSet, basename="transaction")
router.register("billing/charges", ChargeViewSet, basename="charge")

urlpatterns = router.urls + [
    path("billing/pay/", PayView.as_view(), name="billing_pay"),
    path(
        "billing/invoices/<int:pk>/pdf/",
        InvoicePdfView.as_view(),
        name="invoice_pdf",
    ),
    path(
        "billing/webhook/<str:provider>/",
        PaymentWebhookView.as_view(),
        name="billing_webhook",
    ),
]
