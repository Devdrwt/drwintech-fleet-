"""
Convertit telemetry_position en hypertable TimescaleDB (voir ADR 0003).

TimescaleDB impose que la colonne de partitionnement (`time`) appartienne à
toute contrainte UNIQUE/PRIMARY KEY. La PK `id` générée par Django ne l'inclut
pas → on la remplace par une PK composite (id, time) puis on crée l'hypertable.

S'applique uniquement sur la base `telemetry` (routeur — config/db_routers.py).
Nécessite l'image timescale/timescaledb (docker-compose service `timescaledb`).
"""
from django.db import migrations

CREATE = [
    "CREATE EXTENSION IF NOT EXISTS timescaledb;",
    # Remplace la PK simple (id) par une PK composite incluant la colonne de temps.
    "ALTER TABLE telemetry_position DROP CONSTRAINT IF EXISTS telemetry_position_pkey;",
    "ALTER TABLE telemetry_position ADD PRIMARY KEY (id, \"time\");",
    # Création de l'hypertable (migration des données existantes incluse).
    "SELECT create_hypertable('telemetry_position', 'time', "
    "if_not_exists => TRUE, migrate_data => TRUE);",
    # Compression des chunks de plus de 7 jours (économie de stockage).
    "ALTER TABLE telemetry_position SET ("
    "timescaledb.compress, "
    "timescaledb.compress_segmentby = 'device_imei');",
    "SELECT add_compression_policy('telemetry_position', INTERVAL '7 days', "
    "if_not_exists => TRUE);",
    # Rétention : suppression automatique des positions de plus de 12 mois (RGPD).
    "SELECT add_retention_policy('telemetry_position', INTERVAL '12 months', "
    "if_not_exists => TRUE);",
]

REVERSE = [
    "SELECT remove_retention_policy('telemetry_position', if_exists => TRUE);",
    "SELECT remove_compression_policy('telemetry_position', if_exists => TRUE);",
    # Note : reconvertir une hypertable en table simple n'est pas supporté
    # nativement ; ce reverse retire seulement les politiques.
]


class Migration(migrations.Migration):
    dependencies = [
        ("telemetry", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(sql=CREATE, reverse_sql=REVERSE),
    ]
