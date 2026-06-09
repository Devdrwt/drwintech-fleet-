# Sécurité & RGPD — Drwintech Fleet

## 1. Authentification

- **JWT** (SimpleJWT) : access court (15–60 min) + refresh (7 j) avec **rotation** et **blacklist** à la déconnexion.
- Login flexible **email ou téléphone**.
- **Protection brute-force** sur `/auth/token/` (django-ratelimit + verrouillage progressif).
- Mots de passe : Argon2 (hasher Django) ou bcrypt.
- 2FA TOTP optionnel pour les rôles admin/superadmin (phase ultérieure).

## 2. Autorisation (RBAC + objet)

- Rôles : `superadmin` (4) > `admin` (3) > `superviseur`/`technicien`/`comptable`/`support` (2) > `client` (1).
- **Permissions au niveau objet** : un utilisateur ne voit que les véhicules/clients de son périmètre.
- **Commandes device** (couper moteur, redémarrer) = action sensible → permission dédiée + audit + confirmation.
- Composant front `<Can>` + permissions DRF côté backend (jamais de contrôle uniquement côté client).

## 3. Transport & en-têtes

- **HTTPS/TLS 1.2+** obligatoire (Let's Encrypt via Nginx/Traefik).
- HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy.
- CORS restreint aux origines front connues.

## 4. Données au repos

- **Chiffrement** des données sensibles (PII, secrets device, tokens agrégateurs paiement) — `django-fernet-fields` ou pgcrypto.
- Secrets applicatifs via variables d'environnement / coffre (jamais en dur, jamais commités).
- `.env` exclu du versionnement ; `.env.example` fourni.

## 5. Audit & traçabilité

- `audit.AuditLog` **append-only** (pas d'update/delete) dès le jour 1.
- Capture : qui (user), quoi (action), sur quoi (resource), avant/après (changes JSON), d'où (IP/UA), quand.
- Middleware d'audit sur les écritures (POST/PUT/PATCH/DELETE) — **implémenté, pas un placeholder**.

## 6. RGPD / données personnelles

> Les **positions GPS sont des données personnelles**. Traitement encadré.

- **Base légale** : exécution du contrat de service GPS.
- **Rétention** : positions brutes 12 mois (configurable), résumés de trajets plus longtemps, anonymisation au-delà.
- **Droit à l'effacement** : procédure d'effacement/anonymisation d'un client et de ses données télémétriques.
- **Journalisation des accès** aux données de localisation.
- **Minimisation** : ne stocker que les attributs utiles.

## 7. Sécurité du moteur Traccar

- Traccar **non exposé directement** à Internet pour son UI/API : accès via le backend ou réseau privé.
- Seuls les **ports devices** (TCP/UDP) sont exposés, filtrés par firewall.
- Authentification API Traccar via compte de service dédié (secret en coffre).
- Validation des `uniqueId`/IMEI entrants (rejet des devices inconnus si mode strict).

## 8. Sécurité applicative

- Rate limiting global (anon 100/h, auth 1000/h) + spécifique sur endpoints sensibles.
- Validation stricte des entrées (serializers DRF, Zod côté front).
- Protection contre IDOR (permissions objet systématiques).
- Dépendances : audit régulier (`pip-audit`, `npm audit`), Dependabot.
- Webhooks paiement : **vérification de signature** + idempotence.

## 9. Monitoring & réponse

- Logs structurés (loguru / JSON), centralisés.
- Alertes sur échecs d'auth répétés, erreurs de sync, pics anormaux.
- Sauvegardes chiffrées + tests de restauration réguliers.
