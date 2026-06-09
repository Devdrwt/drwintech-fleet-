# Drwintech Fleet — Plan directeur

> Plateforme indépendante de gestion de flotte GPS et de la relation client/abonnement.
> Nom de travail : **Drwintech Fleet** (renommable). Remplace l'ancien DGMS dépendant de GPS-Trace.

---

## 1. Vision & objectifs

Construire une plateforme **100 % indépendante** (plus aucune dépendance à GPS-Trace) qui :

1. **Reçoit directement** les trames des boîtiers GPS sur notre propre infrastructure.
2. Offre le **suivi temps réel** (carte live), l'historique de trajets, les géofences et les alertes.
3. Gère le **métier** : clients/abonnés, parc matériel (boîtiers + SIM), abonnements, paiements (agrégateurs africains), maintenance, reporting.
4. Est **moderne, sécurisée, conforme RGPD** et prête à monter en charge (> 5 000 boîtiers).

### Décisions structurantes (verrouillées)

| Décision | Choix | ADR |
|---|---|---|
| Couche d'ingestion (décodage protocoles) | **Traccar auto-hébergé** (Apache 2.0) | [0001](adr/0001-traccar-as-ingestion-engine.md) |
| Backend métier | **Django + DRF** (Python) | [0002](adr/0002-backend-django-drf.md) |
| Stockage télémétrie | **TimescaleDB** (extension PostgreSQL) | [0003](adr/0003-timescaledb-for-telemetry.md) |
| Cartographie | **MapLibre GL + OpenStreetMap** | [0004](adr/0004-maplibre-osm.md) |
| Style d'architecture | **Monolithe modulaire** (contextes délimités) | [0005](adr/0005-modular-monolith.md) |
| Code | **Repartir de zéro**, en capitalisant sur le modèle métier éprouvé | — |
| Multi-tenant | **Mono-entreprise** (Drwintech), modèle de données non bloquant pour l'avenir | — |

---

## 2. Périmètre

**Inclus** : flotte GPS, télémétrie, géofences/alertes, CRM abonnés, abonnements & paiements, maintenance, notifications, reporting, audit/RGPD, espace client.

**Exclu** : gestion scolaire (SIS) — hors périmètre.

---

## 3. Architecture cible (résumé)

```
[Boîtiers GPS] --TCP/UDP--> [Traccar (Docker)] --REST/WS--> [Backend Django/DRF]
                                   |                              |
                            [TimescaleDB]                   [PostgreSQL]  [Redis]
                            (positions/trips)               (métier)      (cache/broker/pubsub)
                                                                  |
                                                          [Frontend Next.js + MapLibre]
```

Détails complets : [ARCHITECTURE.md](ARCHITECTURE.md).

**Intégration Traccar ↔ métier**
- **Provisioning & commandes** (créer device, envoyer commande) → API REST Traccar.
- **Positions temps réel** → pont WebSocket Traccar → Redis pub/sub → front.
- **Historique/trajets** → TimescaleDB (hypertables + agrégats continus).
- **Lien device ↔ métier** → par **IMEI** (`fleet.GpsUnit.imei == traccar.device.uniqueId`).

---

## 4. Modèle de domaine (contextes délimités)

| Contexte | App Django | Entités clés |
|---|---|---|
| Identity & Access | `accounts` | User, Role, Permission |
| Fleet / Parc | `fleet` | Vehicle, GpsUnit, SimCard, SimRecharge |
| Telemetry | `telemetry` | Position, Trip, DeviceEvent (lecture Traccar → Timescale) |
| Geofencing & Alerts | `geofencing` | Geofence, AlertRule, AlertEvent |
| CRM | `crm` | Client, Contact |
| Billing & Payments | `billing` | Subscription, Invoice, Transaction, Charge |
| Maintenance | `maintenance` | Intervention |
| Notifications | `notifications` | NotificationTemplate, NotificationLog |
| Reporting | `reporting` | (agrégations à la volée) |
| Audit & Compliance | `audit` | AuditLog (append-only), RetentionPolicy |
| Intégration moteur | `integrations` | TraccarSyncLog, client API/WS Traccar |

Schéma détaillé : [DATA-MODEL.md](DATA-MODEL.md).

---

## 5. Feuille de route par phases

### Phase 0 — Cadrage (2–3 sem.)
- [ ] Valider les ADRs et l'architecture.
- [ ] Choisir les **3 premiers modèles de trackers** supportés (ex. Teltonika FMB, Concox GT06, Queclink).
- [ ] Figer le schéma de données positions/événements.
- [ ] Threat model sécurité + politique RGPD/rétention.
- [ ] Repo, CI/CD, docker-compose de dev opérationnels.

### Phase 1 — Ingestion propre (4–6 sem.) ⚠️ *risque attaqué en premier*
- [ ] Traccar auto-hébergé + TimescaleDB en place.
- [ ] **2–3 vrais boîtiers** remontent directement sur notre serveur.
- [ ] Position temps réel validée sur carte MapLibre.
- [ ] Pont WebSocket Traccar → Redis fonctionnel.

### Phase 2 — Socle backend + carte live (4–6 sem.)
- [ ] Backend Django : `accounts` (auth JWT + RBAC), `fleet`, `integrations`.
- [ ] Provisioning device via API Traccar.
- [ ] Page carte temps réel dans le front.

### Phase 3 — Métier (6–10 sem.)
- [ ] `crm` (clients), `billing` (abonnements, factures).
- [ ] Paiements + **webhooks** (Gobipay / Fedapay / Notchpay).
- [ ] Facturation PDF, suspension auto sur impayé.
- [ ] `maintenance` (interventions, déclenchables par télémétrie).

### Phase 4 — Intelligence (4–6 sem.)
- [ ] Géofences, règles d'alertes, événements.
- [ ] Notifications email/SMS/push réelles.
- [ ] Trajets, rapports, dashboards (Recharts).

### Phase 5 — Durcissement & Go-Live
- [ ] Sécurité (pentest interne), RGPD (rétention, effacement).
- [ ] Monitoring (Prometheus/Grafana), tests de charge.
- [ ] Documentation, recette, déploiement production.

**Cible : V1 indépendante et solide en ~4–6 mois.**

---

## 6. Risques & mitigations

| Risque | Impact | Mitigation |
|---|---|---|
| Compatibilité protocole tracker | Élevé | Phase 1 d'abord, vrais devices, s'appuyer sur Traccar (200+ protocoles) |
| Volume de positions (time-series) | Moyen | TimescaleDB, agrégats continus, politique de rétention |
| Sécurité des commandes device | Élevé | Autorisation + audit append-only + double contrôle |
| RGPD (positions = données perso) | Légal | Rétention, effacement, journalisation des accès |
| Dérive de périmètre | Planning | Phases verrouillées, périmètre SIS exclu |

---

## 7. Stack technique

- **Moteur** : Traccar (Java, Docker).
- **Backend** : Django 5 + DRF, Celery, SimpleJWT.
- **Bases** : PostgreSQL (métier) + TimescaleDB (télémétrie), Redis (cache/broker/pubsub).
- **Frontend** : Next.js 14 (App Router), TypeScript, Tailwind, TanStack Query, Zustand, MapLibre GL.
- **Infra** : Docker Compose (dev) → Kubernetes (scale), Nginx/Traefik, Prometheus/Grafana.
