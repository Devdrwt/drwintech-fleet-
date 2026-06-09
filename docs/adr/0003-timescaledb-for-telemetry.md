# ADR 0003 — TimescaleDB pour la télémétrie

- **Statut** : Accepté
- **Date** : 2026-06-09

## Contexte

Une flotte de > 5 000 boîtiers émettant des positions toutes les quelques secondes génère des **millions de lignes/jour**. Une table PostgreSQL classique se dégrade rapidement (taille, index, requêtes d'historique).

## Décision

Stocker les positions et événements télémétriques dans **TimescaleDB** (extension PostgreSQL) sous forme d'**hypertables**. Les données métier restent dans une base PostgreSQL standard.

## Justification

- Hypertables partitionnées par temps → insertion et requêtes d'historique performantes.
- **Compression** automatique des données anciennes.
- **Rétention** automatique (drop des chunks expirés) → conformité RGPD facilitée.
- **Continuous aggregates** → résumés de trajets pré-calculés (distance, durée, vitesse).
- Reste du SQL/Postgres : pas de nouvelle techno radicale à apprendre.

## Alternatives écartées

- **Postgres simple** : ne tient pas la volumétrie time-series. ❌
- **InfluxDB / ClickHouse** : performants mais ajoutent une base hétérogène + opérations supplémentaires. 🟡

## Conséquences

- ✅ Performance et rétention maîtrisées.
- ⚠️ Deux instances Postgres à exploiter (métier + Timescale) — séparation nette des préoccupations.
