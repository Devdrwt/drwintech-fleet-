# Architecture — Drwintech Fleet

## 1. Vue d'ensemble

Système composé de **deux moteurs** clairement séparés :

1. **Moteur d'ingestion télémétrique** = Traccar (boîte noire que nous possédons, conteneur Java).
2. **Plateforme métier** = notre code (Django/DRF + Next.js), où vit toute la valeur ajoutée.

Les deux communiquent par **contrat explicite** (API REST + WebSocket), jamais par couplage de code.

```
                         ┌─────────────────────────────────────────────┐
   Boîtiers GPS  ─TCP/UDP─▶            TRACCAR (Docker)                  │
   (Teltonika,            │  Netty pipeline · 200+ décodeurs ·          │
    Concox/GT06,          │  ACK · file de commandes sortantes          │
    Queclink…)            └───────┬───────────────────────┬─────────────┘
                                  │ REST API              │ WebSocket (positions)
                                  │ (provisioning,        │
                                  │  commandes)           ▼
                                  │                ┌──────────────┐
                                  │                │ WS Bridge    │ (service léger)
                                  │                │ Traccar→Redis│
                                  ▼                └──────┬───────┘
                         ┌────────────────────────────────┼───────────────────┐
                         │           BACKEND DJANGO/DRF    │ (monolithe modulaire)
                         │  accounts · fleet · telemetry · │ geofencing · crm   │
                         │  billing · maintenance · notifs ·│ reporting · audit │
                         │  integrations (client Traccar)  │                    │
                         └───┬───────────────┬─────────────┴──────┬─────────────┘
                  PostgreSQL │     Redis      │   TimescaleDB      │ Celery workers
                  (métier)   │ (cache/broker/ │  (positions/trips) │ (jobs async)
                             │  pubsub)       │                    │
                                             ▼
                         ┌────────────────────────────────────────────┐
                         │   FRONTEND Next.js 14 + MapLibre GL          │
                         │   back-office · espace client · carte live   │
                         └────────────────────────────────────────────┘
```

## 2. Flux de données

### 2.1 Position temps réel (lecture)
1. Le boîtier envoie une trame → Traccar la décode.
2. Traccar émet la position sur son **WebSocket**.
3. Le **WS Bridge** (petit service) s'abonne, normalise, et publie sur **Redis pub/sub** (`positions:{deviceId}`).
4. Le backend Django (via Channels ou un consumer WS) relaie au front abonné.
5. Le front met à jour le marqueur sur la carte MapLibre.

### 2.2 Persistance des trajets (écriture)
- Le WS Bridge (ou un worker Celery) écrit les positions en **TimescaleDB** (hypertable `positions`).
- Des **agrégats continus** (continuous aggregates) calculent les résumés de trajets (distance, durée, vitesse max) sans recalcul à la lecture.

### 2.3 Provisioning d'un boîtier (commande)
1. Admin crée un `GpsUnit` (IMEI) dans le backend.
2. Le backend appelle l'**API REST Traccar** pour créer le `device` correspondant (`uniqueId = imei`).
3. Lien établi : toute position de ce device est rattachée au `GpsUnit` → `Vehicle` → `Client`.

### 2.4 Commande sortante (ex. couper moteur)
1. Action déclenchée côté back-office (autorisée par RBAC + auditée).
2. Backend → API Traccar `POST /commands/send`.
3. Traccar place la commande dans sa file et l'envoie au boîtier.

## 3. Séparation des responsabilités

| Responsabilité | Traccar | Backend Django |
|---|---|---|
| Décodage protocoles | ✅ | ❌ |
| Positions temps réel | ✅ (émet) | relaie |
| File de commandes device | ✅ | déclenche |
| Clients / abonnements / paiements | ❌ | ✅ |
| RBAC / audit / RGPD métier | ❌ | ✅ |
| Maintenance / reporting | ❌ | ✅ |
| Géofences | possible des 2 côtés | **maître** (logique métier) |

> Règle : Traccar est traité comme un **fournisseur de télémétrie remplaçable**. Aucune logique métier ne vit dedans. Si un jour on internalise le moteur (Option C), seul le contexte `integrations` change.

## 4. Découpage en modules (monolithe modulaire)

Chaque app Django est un **contexte délimité** avec sa frontière :
- Modèles, serializers, services, vues, urls propres.
- Communication inter-modules via **services** (pas d'import croisé de vues).
- Permet une extraction ultérieure en microservice si besoin, sans réécriture.

## 5. Temps réel & scalabilité

- **WebSocket** : Django Channels + Redis channel layer.
- **TimescaleDB** : hypertables partitionnées par temps, compression, rétention automatique.
- **Celery** : tâches async (écriture batch positions, calcul trajets, notifications, webhooks).
- **Montée en charge** : services stateless derrière un load balancer ; Traccar scalable verticalement d'abord, puis sharding par plage de devices.

## 6. Environnements

| Env | Bases | Traccar | Notes |
|---|---|---|---|
| Dev | Postgres + Timescale (Docker) | Docker | docker-compose tout-en-un |
| Staging | managé ou VM | VM dédiée | données de test |
| Prod | Postgres HA + Timescale | VM/cluster dédié | TLS, monitoring, backups |
