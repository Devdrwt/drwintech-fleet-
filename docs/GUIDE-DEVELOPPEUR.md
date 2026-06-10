# Guide développeur — Drwintech Fleet

Guide pratique pour installer, lancer, tester et contribuer au projet au quotidien.
Pour la vision d'ensemble, voir [PLAN.md](PLAN.md) et [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 1. Prérequis

| Outil | Version | Vérifier |
|---|---|---|
| Python | 3.13 (3.13 = version CI) | `python --version` |
| Node.js | 20 LTS | `node --version` |
| Docker + Docker Compose | récent | `docker compose version` |
| Git | récent | `git --version` |

Sous Windows, les commandes shell ci-dessous existent en deux variantes (`bash` / PowerShell)
là où elles diffèrent.

---

## 2. Installation complète (première fois)

### 2.1 Cloner et configurer l'environnement

```bash
git clone https://github.com/Devdrwt/drwintech-fleet.git
cd drwintech-fleet
cp .env.example .env          # PowerShell : Copy-Item .env.example .env
```

Le fichier `.env` n'est **jamais commité**. Renseigne au minimum un `SECRET_KEY` pour le dev
et, si tu testes les paiements, les clés `FEDAPAY_*` (sandbox).

### 2.2 Lancer l'infrastructure (Docker)

```bash
docker compose up -d
```

Services et ports (⚠️ ports décalés pour éviter les collisions avec un Postgres/Redis local) :

| Service | Port hôte | Rôle |
|---|---|---|
| Traccar | 8082 | Moteur d'ingestion GPS (UI/API) |
| PostgreSQL | **5440** | Base métier (`fleet`) |
| TimescaleDB | **5434** | Base télémétrie (`fleet_telemetry`) |
| Redis | **6381** | Cache / broker Celery / pub-sub |

> Ces ports correspondent à `.env.example` (`DB_PORT=5440`, `TSDB_PORT=5434`,
> `REDIS_URL=...:6381`). Si tu les changes dans `docker-compose.yml`, change aussi `.env`.

### 2.3 Backend (Django + DRF)

```bash
cd backend
python -m venv venv
source venv/bin/activate            # PowerShell : venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate                         # base métier (PostgreSQL)
python manage.py migrate --database=telemetry    # base télémétrie (TimescaleDB)
python manage.py createsuperuser
python manage.py runserver 8000
```

- API : http://localhost:8000/api/v1/
- Doc OpenAPI (drf-spectacular) : http://localhost:8000/api/docs/

> ⚠️ Phase 1 : transformer `telemetry.Position` en hypertable Timescale via une migration SQL
> (`SELECT create_hypertable('telemetry_position', 'time')`). Voir
> [adr/0003-timescaledb-for-telemetry.md](adr/0003-timescaledb-for-telemetry.md).

### 2.4 Frontend (Next.js 14)

```bash
cd frontend
cp .env.local.example .env.local    # PowerShell : Copy-Item .env.local.example .env.local
npm install
npm run dev                          # http://localhost:3000
```

`NEXT_PUBLIC_API_URL` doit pointer vers `http://localhost:8000/api/v1`.

### 2.5 Traccar

- UI/API : http://localhost:8082 — **changer le login par défaut immédiatement**.
- En prod : ne **jamais** exposer l'UI/API publiquement (accès via backend / réseau privé).
  Voir [adr/0001-traccar-as-ingestion-engine.md](adr/0001-traccar-as-ingestion-engine.md).

---

## 3. Lancement quotidien (déjà installé)

```bash
docker compose up -d                                   # infra
cd backend && source venv/bin/activate && python manage.py runserver 8000
cd frontend && npm run dev
# (optionnel) worker async :
cd backend && celery -A config worker -l info
```

---

## 4. Tests

La CI exécute `pytest` sur le backend et `next build` sur le frontend (voir §6).

### 4.1 Backend

```bash
cd backend
source venv/bin/activate
pytest                       # config : pytest.ini (settings = config.settings.development)
pytest tests/test_scoping.py # un seul fichier
pytest -k recurring          # par mot-clé
pytest -x -vv                # stop au 1er échec, verbeux
```

Suites présentes ([backend/tests/](../backend/tests/)) :

| Fichier | Couvre |
|---|---|
| `test_scoping.py` | Cloisonnement multi-tenant (un client ne voit que ses données) |
| `test_payments.py` | Initiation paiement + webhook (signature HMAC FedaPay) |
| `test_recurring.py` | Abonnements récurrents / facturation automatique |

> Les tests tournent sur une base de test gérée par `pytest-django`. La CI provisionne
> TimescaleDB + Redis ; en local, `docker compose up -d` suffit.

### 4.2 Frontend

```bash
cd frontend
npm run lint     # ESLint (next lint)
npm run build    # ce que vérifie la CI
```

---

## 5. Conventions de code

### 5.1 Backend — monolithe modulaire

Chaque app de [backend/apps/](../backend/apps/) est un **contexte délimité** (`accounts`, `crm`,
`fleet`, `telemetry`, `geofencing`, `billing`, `maintenance`, `notifications`, `reporting`,
`audit`, `integrations`). Règles :

- **Pas d'import croisé de vues** entre apps. La communication inter-modules passe par des
  **services** (`apps/<module>/services.py`). Voir
  [adr/0005-modular-monolith.md](adr/0005-modular-monolith.md).
- Deux bases de données → **db routers** ([backend/config/db_routers.py](../backend/config/db_routers.py)) :
  le métier va sur `default` (Postgres), la télémétrie sur `telemetry` (Timescale).
  Toute écriture télémétrie doit cibler `using='telemetry'`.
- Lint/format : **ruff** (`ruff check .`, `ruff format .`).
- Toute donnée client doit respecter le **cloisonnement** : filtrer par le tenant courant.
  Ne jamais renvoyer un queryset non scopé (cf. `test_scoping.py`).

### 5.2 Frontend

- Next.js 14 **App Router** ([frontend/src/app/](../frontend/src/app/)), i18n via `next-intl`
  (locale par défaut `fr`).
- Data fetching : `@tanstack/react-query` + `axios` (base = `NEXT_PUBLIC_API_URL`).
- Carte : `maplibre-gl` (OSM, pas de SaaS). Voir
  [adr/0004-maplibre-osm.md](adr/0004-maplibre-osm.md).

### 5.3 Ajouter une nouvelle app Django

```bash
cd backend
python manage.py startapp <nom> apps/<nom>
```

Puis : déclarer l'app dans `config/settings/base.py` (`INSTALLED_APPS`), créer
`apps/<nom>/services.py` pour l'API inter-module, brancher les routes dans `config/urls.py`,
et générer la migration :

```bash
python manage.py makemigrations <nom>
python manage.py migrate
```

---

## 6. Intégration continue (CI)

Workflow : [.github/workflows/ci.yml](../.github/workflows/ci.yml). Déclenché à chaque
**push / PR** sur `dev`, `staging`, `main`.

| Job | Étapes |
|---|---|
| **backend** | Python 3.13 · services `timescaledb` + `redis:7` (health-checks) · `pip install -r requirements.txt` · `pytest` |
| **frontend** | Node 20 (cache npm) · `npm ci` · `npm run build` |

Les variables d'environnement de la CI reproduisent `.env` (préfixes `DB_`, `TSDB_`,
`REDIS_URL`, `CELERY_BROKER_URL`, `SECRET_KEY`) et concordent avec
[config/settings/base.py](../backend/config/settings/base.py).

---

## 7. Flux Git & branches

```
feature/* ──▶ dev ──▶ staging ──▶ main
```

| Branche | Rôle |
|---|---|
| `dev` | Intégration courante. On y merge les `feature/*`. |
| `staging` | Pré-production / recette. |
| `main` | Production. |

Workflow type :

```bash
git checkout dev && git pull
git checkout -b feature/ma-fonctionnalite
# ... commits ...
git push -u origin feature/ma-fonctionnalite
# Ouvrir une PR vers dev (la CI tourne automatiquement)
```

**Convention de commits** : préfixes type Conventional Commits déjà en usage dans l'historique
(`feat(...)`, `fix(...)`, `test+secu:`, `ci:`, `chore:`). Garder un titre court et descriptif.

> Remote : `origin` → `https://github.com/Devdrwt/drwintech-fleet.git`.
> Auth en HTTPS via Git Credential Manager (une fenêtre de connexion peut s'ouvrir au 1er push).

---

## 8. Dépannage

| Symptôme | Cause probable / solution |
|---|---|
| `connection refused` Postgres/Redis au lancement backend | `docker compose up -d` pas lancé, ou ports `.env` ≠ ports `docker-compose.yml` |
| `pytest` : `no tests ran` | Lancer depuis `backend/` (où se trouve `pytest.ini`) |
| Webhook paiement rejeté (401/403) | Signature HMAC FedaPay invalide — vérifier `FEDAPAY_SECRET_KEY` |
| Écriture télémétrie va dans la mauvaise base | Oubli de `using='telemetry'` / mauvais routage `db_routers.py` |
| `#` dans une valeur `.env` tronque la valeur | Mettre la valeur entre quotes (ex. `TRACCAR_SERVICE_PASSWORD='...#...'`) |
| `next build` échoue sur `NEXT_PUBLIC_API_URL` | Variable manquante dans `.env.local` |

---

## 9. Documentation liée

| Doc | Contenu |
|---|---|
| [PLAN.md](PLAN.md) | Plan directeur, périmètre, feuille de route par phases |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture détaillée, flux de données |
| [DATA-MODEL.md](DATA-MODEL.md) | Modèle de données (métier + télémétrie) |
| [SECURITY.md](SECURITY.md) | Sécurité & conformité RGPD |
| [adr/](adr/) | Décisions d'architecture (ADR) |
