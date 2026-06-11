"""
Agrégations de reporting (à la volée, pas de modèle persistant — voir PLAN §4).

Toutes les fonctions acceptent un `client_id` optionnel : s'il est fourni, les
agrégats sont cloisonnés à ce client (espace client) ; sinon ils sont globaux
(back-office). Cf. cloisonnement dans apps.accounts.scoping.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.billing.models import Invoice, Transaction
from apps.crm.models import Client


def quarter_start(d: date) -> date:
    """Premier jour du trimestre contenant `d`."""
    first_month = ((d.month - 1) // 3) * 3 + 1
    return d.replace(month=first_month, day=1)


def _shift_months(d: date, months: int) -> date:
    """Décale `d` (au 1er du mois) de `months` (peut être négatif)."""
    total = (d.year * 12 + (d.month - 1)) + months
    return date(total // 12, total % 12 + 1, 1)


def revenue_between(start: date, end: date, client_id=None) -> Decimal:
    """CA encaissé (transactions réussies) sur l'intervalle [start, end[."""
    qs = Transaction.objects.filter(
        status=Transaction.Status.SUCCESS,
        paid_at__isnull=False,
        paid_at__date__gte=start,
        paid_at__date__lt=end,
    )
    if client_id:
        qs = qs.filter(client_id=client_id)
    return qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")


def monthly_revenue(months: int = 12, client_id=None) -> list[dict]:
    """Série du CA encaissé sur les `months` derniers mois (mois manquants à 0)."""
    today = timezone.localdate()
    this_month = today.replace(day=1)
    start = _shift_months(this_month, -(months - 1))

    qs = Transaction.objects.filter(
        status=Transaction.Status.SUCCESS,
        paid_at__isnull=False,
        paid_at__date__gte=start,
    )
    if client_id:
        qs = qs.filter(client_id=client_id)

    rows = (
        qs.annotate(m=TruncMonth("paid_at"))
        .values("m")
        .annotate(total=Sum("amount"))
    )
    by_month = {r["m"].date().replace(day=1): (r["total"] or Decimal("0")) for r in rows}

    series = []
    for i in range(months):
        m = _shift_months(start, i)
        series.append({"month": m.isoformat(), "total": by_month.get(m, Decimal("0"))})
    return series


def unpaid_summary(client_id=None) -> dict:
    """Factures en retard (impayés)."""
    qs = Invoice.objects.filter(status=Invoice.Status.OVERDUE)
    if client_id:
        qs = qs.filter(client_id=client_id)
    agg = qs.aggregate(total=Sum("amount"))
    return {"count": qs.count(), "total": agg["total"] or Decimal("0")}


def new_clients(days: int = 30, client_id=None) -> int:
    """Nombre de clients créés dans la fenêtre (évolution clients)."""
    if client_id:
        return 0  # un utilisateur client ne compte pas les nouveaux clients
    since = timezone.now() - timedelta(days=days)
    return Client.objects.filter(created_at__gte=since).count()
