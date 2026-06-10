# Drwintech Fleet

> Plateforme **indépendante** de gestion de flotte GPS — suivi temps réel, CRM abonnés,
> abonnements/paiements, maintenance, reporting. Aucune dépendance à un SaaS tiers (ex. GPS-Trace).

Nom de travail : **Drwintech Fleet** (renommable). Remplace l'ancien DGMS.

## 🎯 Principe

L'indépendance repose sur le fait de **recevoir directement les trames des boîtiers GPS**
sur notre propre infrastructure. La couche de décodage des protocoles est assurée par
**Traccar auto-hébergé** (open source, Apache 2.0), traité comme un fournisseur de
télémétrie **remplaçable**. Toute la valeur métier vit dans notre code.

```
[Boîtiers GPS] --TCP/UDP--> [Traccar] --REST/WS--> [Backend Django/DRF] --> [Next.js + MapLibre]
                                |                          |
                          [TimescaleDB]            [PostgreSQL]  [Redis]
```

## 📚 Documentation

| Doc | Contenu |
|---|---|
| [docs/PLAN.md](docs/PLAN.md) | Plan directeur, périmètre, feuille de route par phases |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture détaillée, flux de données |
| [docs/DATA-MODEL.md](docs/DATA-MODEL.md) | Modèle de données (métier + télémétrie) |
| [docs/SECURITY.md](docs/SECURITY.md) | Sécurité & conformité RGPD |
| [docs/adr/](docs/adr/) | Décisions d'architecture (ADR) |

## 🗂 Structure

```
drwintech-fleet/
├── docker-compose.yml      # Traccar + Postgres + TimescaleDB + Redis
├── infra/traccar/          # config Traccar
├── backend/                # Django + DRF (monolithe modulaire)
│   ├── config/             # settings, urls, celery, asgi, routers
│   └── apps/               # accounts, crm, fleet, telemetry, geofencing,
│                           # billing, maintenance, notifications,
│                           # reporting, audit, integrations
├── frontend/               # Next.js 14 + MapLibre
└── docs/                   # plan, architecture, ADRs
```

## 🚀 Démarrage (développement)

### 1. Infrastructure
```bash
cp .env.example .env
docker compose up -d        # Traccar (8082), Postgres (5432), Timescale (5433), Redis (6379)
```

### 2. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # (Windows : venv\Scripts\activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py migrate --database=telemetry      # base télémétrie
python manage.py createsuperuser
python manage.py runserver 8000
# API docs : http://localhost:8000/api/docs/
```

> ⚠️ Étape Phase 1 : transformer `telemetry.Position` en hypertable Timescale
> (migration SQL `SELECT create_hypertable('telemetry_position', 'time')`).

### 3. Frontend
```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev                 # http://localhost:3000
```

### 4. Traccar
- UI/API : http://localhost:8082 (login par défaut à changer immédiatement).
- En prod : **ne pas exposer** l'UI/API publiquement (accès via backend / réseau privé).

## 🛣 Feuille de route

Voir [docs/PLAN.md](docs/PLAN.md). Cible : **V1 indépendante en ~4–6 mois**.
La Phase 1 (ingestion propre avec de vrais boîtiers) attaque le risque principal en premier.

## 🔁 Intégration continue (CI)

Workflow GitHub Actions : [.github/workflows/ci.yml](.github/workflows/ci.yml).
À chaque push / PR sur `dev`, `staging`, `main` :
- **Backend** : `pytest` (services TimescaleDB + Redis provisionnés par la CI).
- **Frontend** : `npm ci` + `next build`.

**Flux de branches** : `dev` → `staging` → `main` (mêmes conventions que les dépôts SPF).

**Activation** (le dépôt est local pour l'instant) :
```bash
# 1. Créer le dépôt sur GitHub (ex. github.com/<org>/drwintech-fleet)
# 2. Lier et pousser les branches
git remote add origin git@github.com:<org>/drwintech-fleet.git
git push -u origin main staging dev
```
La CI se déclenche automatiquement dès le premier push.

## 📄 Licence

Propriétaire — Drwintech. Composant Traccar sous Apache 2.0 (auto-hébergé).
