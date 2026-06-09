# ADR 0002 — Backend métier en Django + DRF

- **Statut** : Accepté
- **Date** : 2026-06-09

## Contexte

Nouveau backend à construire de zéro pour la couche métier (clients, parc, paiements, maintenance, reporting). L'équipe a déjà livré l'ancien DGMS en Django.

## Décision

**Django 5 + Django REST Framework**, avec Celery (tâches async), SimpleJWT (auth), Channels (temps réel).

## Justification

- **Familiarité de l'équipe** → livraison rapide, moins de risque.
- DRF mature pour les API REST ; écosystème riche (permissions, serializers, pagination).
- Celery déjà éprouvé pour l'async (webhooks, notifications, écriture batch).
- ORM solide pour le modèle métier ; intégration TimescaleDB possible (Postgres).

## Alternatives écartées

- **NestJS (TypeScript)** : TS de bout en bout, excellent en temps réel, mais courbe d'apprentissage si l'équipe vient de Python. 🟡
- **Go** : performance maximale mais écosystème métier moins riche, démarrage plus lent. 🟡

## Conséquences

- ✅ Vélocité élevée, capitalisation sur l'expérience DGMS.
- ⚠️ Le temps réel haute fréquence reste géré par le WS Bridge + Channels + Redis (Python suffisant à notre échelle ; réévaluable si > dizaines de milliers de devices).
