# Modèle de données — Drwintech Fleet

> Capitalise sur le modèle métier éprouvé de l'ancien DGMS, nettoyé et étendu pour l'indépendance télémétrique.

## 1. Diagramme entités-relations (logique)

```
accounts.User ──N:1── accounts.Role
      │
      └──(optionnel)──1:1── crm.Client            # compte espace client

crm.Client ──1:N── crm.Contact
   │
   ├──1:N── fleet.Vehicle ──1:1── fleet.GpsUnit ──1:1── fleet.SimCard ──1:N── fleet.SimRecharge
   │                                   │
   │                                   └──(IMEI)── [Traccar device]
   │
   ├──1:N── billing.Subscription ──1:N── billing.Invoice
   ├──1:N── billing.Transaction          (Gobipay/Fedapay/Notchpay)
   └──1:N── maintenance.Intervention ──N:1── fleet.GpsUnit

telemetry.Position   (TimescaleDB hypertable, clé = device_imei + time)
telemetry.Trip       (résumé, agrégat continu)
telemetry.DeviceEvent

geofencing.Geofence ──1:N── geofencing.AlertRule ──1:N── geofencing.AlertEvent
notifications.NotificationTemplate / NotificationLog
billing.Charge       (dépenses internes)
audit.AuditLog       (append-only)
```

## 2. Entités métier (PostgreSQL)

### accounts.Role
| Champ | Type | Notes |
|---|---|---|
| code | str unique | `superadmin`, `admin`, `superviseur`, `technicien`, `comptable`, `support`, `client` |
| name | str | libellé |
| level | int | hiérarchie (1=user … 4=superadmin) |

### accounts.User (AbstractUser)
| Champ | Type | Notes |
|---|---|---|
| email | email unique | login principal |
| phone | str | login alternatif |
| role | FK Role | RBAC |
| client | FK crm.Client (null) | pour l'espace client |

### crm.Client
| Champ | Type | Notes |
|---|---|---|
| name | str | |
| client_type | enum | `individual` / `company` |
| status | enum | `active` / `suspended` / `inactive` / `terminated` |
| email, phone, address, city, country | str | |
| outstanding_balance | decimal | encours dû (XOF) |
| subscription_end_date | date | |

### fleet.Vehicle
| Champ | Type | Notes |
|---|---|---|
| client | FK Client | |
| name / plate | str | immatriculation |
| type | enum | voiture, moto, camion, engin… |

### fleet.GpsUnit (boîtier)
| Champ | Type | Notes |
|---|---|---|
| vehicle | FK Vehicle (null) | véhicule équipé |
| client | FK Client (null) | null si en stock |
| **imei** | str unique | = `traccar.device.uniqueId` |
| traccar_device_id | int (null) | id côté Traccar |
| serial_number, brand, model_name | str | |
| status | enum | `in_stock` / `active` / `suspended` / `maintenance` / `terminated` / `inactive` |
| installed_at | date | |

### fleet.SimCard / fleet.SimRecharge
- `SimCard` : iccid (unique), phone_number, operator, status, data_credit_mb, OneToOne → GpsUnit.
- `SimRecharge` : sim_card FK, amount, currency, recharged_at, reference, created_by.

### billing.Subscription / Invoice / Transaction / Charge
- `Subscription` : client FK, plan, amount, currency (XOF), start/end, status.
- `Invoice` : subscription/client FK, number, amount, pdf_url, status, due_date.
- `Transaction` : client FK, provider (`gobipay`/`fedapay`/`notchpay`), external_id, amount, status (`pending`/`success`/`failed`/`cancelled`), payment_url, raw_response, paid_at.
- `Charge` : category, amount, currency, charge_date, created_by (dépenses internes).

### maintenance.Intervention
- gps_unit FK, type (`preventive`/`corrective`/`replacement`), status (`open`/`in_progress`/`completed`/`cancelled`), description, scheduled_at, completed_at.
- **Déclenchable par télémétrie** (seuil odomètre/heures moteur).

### audit.AuditLog (append-only)
- user FK, action, resource_type, resource_id, changes (JSON), ip_address, user_agent, created_at.
- Pas de update/delete autorisés (immuable).

## 3. Entités télémétrie (TimescaleDB)

### telemetry.Position (hypertable)
| Champ | Type | Notes |
|---|---|---|
| time | timestamptz | clé de partition (hypertable) |
| device_imei | str | index |
| latitude, longitude | float | |
| speed, course, altitude | float | |
| attributes | jsonb | ignition, battery, fuel, etc. |

Politique : compression après 7 j, rétention configurable (ex. 12 mois positions brutes).

### telemetry.Trip (continuous aggregate)
- device_imei, start_time, end_time, distance_km, duration_s, max_speed, avg_speed.

### telemetry.DeviceEvent
- device_imei, time, type (`ignitionOn`, `geofenceEnter`, `overspeed`…), payload jsonb.

## 4. Géofences & alertes

- `Geofence` : name, area (GeoJSON polygon/circle), client FK (null = global).
- `AlertRule` : geofence FK (null), type (`enter`/`exit`/`overspeed`/`low_battery`/`sim_low_balance`), threshold, channels (email/sms/push).
- `AlertEvent` : rule FK, device_imei, triggered_at, payload, notified (bool).

## 5. Règles métier clés

1. `GpsUnit.imei` = identité partagée avec Traccar (source de liaison).
2. Encours client = somme des factures impayées.
3. Suspension auto si `outstanding_balance > 0` et délai de grâce dépassé → `Client.status = suspended` + commande Traccar optionnelle.
4. Position = donnée personnelle (RGPD) → rétention + effacement sur demande.
5. Audit immuable sur toute action sensible.
