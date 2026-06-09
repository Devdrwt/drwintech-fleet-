"""
Routeur de base de données : dirige les modèles de l'app `telemetry`
vers la base TimescaleDB, le reste vers la base métier (default).
Voir ADR 0003.
"""

TELEMETRY_APP = "telemetry"
TELEMETRY_DB = "telemetry"


class TelemetryRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == TELEMETRY_APP:
            return TELEMETRY_DB
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == TELEMETRY_APP:
            return TELEMETRY_DB
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        # Pas de relations FK cross-base (télémétrie liée par IMEI, pas par FK).
        labels = {obj1._meta.app_label, obj2._meta.app_label}
        if TELEMETRY_APP in labels and len(labels) > 1:
            return False
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == TELEMETRY_APP:
            return db == TELEMETRY_DB
        return db == "default"
