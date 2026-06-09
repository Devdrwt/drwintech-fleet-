"""
Cloisonnement des données par client (object-level — voir SECURITY.md).

Règle : si l'utilisateur est rattaché à un client (`user.client_id` non nul),
il ne voit que les objets de SON client. Les utilisateurs back-office
(client_id nul : admin, support, etc.) voient tout.

Usage : mixin sur une vue DRF, avec `client_filter` = chemin ORM vers le client.
"""


class ClientScopedMixin:
    # Chemin de filtrage ORM vers la PK du client (surchargé par vue).
    client_filter = "client_id"

    def get_queryset(self):
        qs = super().get_queryset()
        client_id = getattr(self.request.user, "client_id", None)
        if client_id:
            return qs.filter(**{self.client_filter: client_id})
        return qs


def client_id_of(request):
    return getattr(request.user, "client_id", None)
