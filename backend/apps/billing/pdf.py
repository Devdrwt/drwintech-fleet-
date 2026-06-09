"""Génération de la facture en PDF (reportlab)."""
from io import BytesIO

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def render_invoice_pdf(invoice) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # En-tête
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20 * mm, h - 25 * mm, "Drwintech Fleet")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, h - 32 * mm, "Facture")

    # Numéro + statut
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, h - 45 * mm, f"Facture n° {invoice.number}")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, h - 52 * mm, f"Statut : {invoice.get_status_display()}")
    if invoice.due_date:
        c.drawString(20 * mm, h - 58 * mm, f"Échéance : {invoice.due_date}")

    # Client
    client = invoice.client
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, h - 72 * mm, "Client")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, h - 78 * mm, client.name)
    if client.email:
        c.drawString(20 * mm, h - 84 * mm, client.email)

    # Montant
    c.setFont("Helvetica-Bold", 14)
    c.drawString(
        20 * mm, h - 105 * mm, f"Montant : {invoice.amount} {invoice.currency}"
    )

    # Pied de page
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(
        20 * mm, 15 * mm, f"Devise : {settings.DEFAULT_CURRENCY} — Document généré automatiquement."
    )

    c.showPage()
    c.save()
    return buffer.getvalue()
