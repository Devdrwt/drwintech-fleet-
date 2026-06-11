# Déploiement — Drwintech Fleet (VPS Hostinger, AlmaLinux 9)

Cible : VPS partagé `69.62.108.213` (srv760780.hstgr.cloud), pattern maison Drwintech
(image Docker → GHCR → conteneurs derrière le nginx de l'hôte + TLS certbot).

- **Front** : https://fleet.drwintech.com → conteneur Next.js (`127.0.0.1:3001`)
- **API** : https://api-fleet.drwintech.com → conteneur Django/daphne (`127.0.0.1:8012`, HTTP + WebSocket)
- **Traccar** : interne uniquement (UI non exposée) ; ports boîtiers publiés : `5023` (GT06), `5027` (Teltonika), `5028` (Queclink).

## Artefacts

| Fichier | Rôle |
|---|---|
| [backend/Dockerfile](../backend/Dockerfile) | Image API/celery/ws-bridge (daphne, ASGI) |
| [backend/docker-entrypoint.sh](../backend/docker-entrypoint.sh) | Migrations (2 bases) + collectstatic + superuser (si `RUN_MIGRATIONS=1`) |
| [frontend/Dockerfile](../frontend/Dockerfile) | Image Next.js standalone |
| [docker-compose.prod.yml](../docker-compose.prod.yml) | 9 services + `mem_limit` (VPS partagé) |
| [.env.production.example](../.env.production.example) | Variables prod (à copier en `.env`) |
| [infra/nginx/](../infra/nginx/) | vhosts `fleet` + `api-fleet` |
| [.github/workflows/deploy.yml](../.github/workflows/deploy.yml) | Build+push GHCR + deploy runner |

## Prérequis (actions hors-code)

1. **DNS** — créer chez le registrar de `drwintech.com` :
   ```
   fleet      A   69.62.108.213
   api-fleet  A   69.62.108.213
   ```
   Vérifier : `dig +short fleet.drwintech.com` doit renvoyer `69.62.108.213`.

2. **Runner self-hosted** (pour le deploy automatique) — les runners existants sont liés
   à d'autres dépôts ; en enregistrer un pour `drwintech-fleet` avec le label `fleet-vps` :
   ```bash
   # Token : repo drwintech-fleet → Settings → Actions → Runners → New self-hosted runner
   mkdir -p /opt/fleet-runner && cd /opt/fleet-runner
   curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64.tar.gz
   tar xzf actions-runner.tar.gz
   ./config.sh --url https://github.com/Devdrwt/drwintech-fleet --token <TOKEN> --labels fleet-vps --unattended
   ./svc.sh install && ./svc.sh start
   ```

## Bootstrap (premier déploiement, sur le VPS)

```bash
# 1. Cloner
git clone https://github.com/Devdrwt/drwintech-fleet.git /opt/drwintech-fleet
cd /opt/drwintech-fleet

# 2. Config : générer les secrets
cp .env.production.example .env
sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -base64 48 | tr -d '\n=/+')|" .env
sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 18)|" .env
sed -i "s|^TSDB_PASSWORD=.*|TSDB_PASSWORD=$(openssl rand -hex 18)|" .env
sed -i "s|^DJANGO_SUPERUSER_PASSWORD=.*|DJANGO_SUPERUSER_PASSWORD=$(openssl rand -hex 12)|" .env
# (renseigner ensuite les clés paiement FEDAPAY_*, VAPID_*, TRACCAR_SERVICE_PASSWORD)

# 3. Images : soit pull depuis GHCR (après un run de la CI), soit build local
docker compose -f docker-compose.prod.yml build      # ou: ... pull
docker compose -f docker-compose.prod.yml up -d

# 4. nginx + TLS
cp infra/nginx/fleet.drwintech.com.conf      /etc/nginx/conf.d/
cp infra/nginx/api-fleet.drwintech.com.conf  /etc/nginx/conf.d/
nginx -t && systemctl reload nginx
certbot --nginx -d fleet.drwintech.com -d api-fleet.drwintech.com --redirect -n --agree-tos -m admin@drwintech.com
```

## Déploiements suivants

Push sur `main` → la CI build+push les images sur GHCR puis le runner `fleet-vps`
exécute `git pull && docker compose pull && up -d`. À défaut de runner, relancer le
bloc « Images » + `up -d` du bootstrap à la main.

## Notes VPS partagé

- **RAM** : ~3 Go libres. Chaque service est borné par `mem_limit`. Surveiller `docker stats`.
- **Ports déjà pris** : 80/443 (nginx), 8000, 8011, 3000/3100/3300, 5000/5001, 5432, 3306.
  Fleet utilise `8012` (api) et `3001` (front) en loopback — ne pas réutiliser ailleurs.
- **Firewall** : `ufw` inactif ; les ports boîtiers Traccar (5023/5027/5028) sont donc joignables.
