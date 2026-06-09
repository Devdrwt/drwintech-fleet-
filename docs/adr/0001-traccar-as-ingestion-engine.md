# ADR 0001 — Traccar comme moteur d'ingestion télémétrique

- **Statut** : Accepté
- **Date** : 2026-06-09

## Contexte

L'ancien DGMS dépendait de **GPS-Trace Partner Panel** (SaaS tiers payant) : pas de temps réel, aucun contrôle de la donnée, verrou fournisseur. L'objectif est l'**indépendance totale** : recevoir directement les trames des boîtiers GPS.

Le défi : chaque tracker parle un **protocole binaire propriétaire** (Teltonika, Concox/GT06, Queclink, Coban…). Écrire et maintenir ces décodeurs est un travail de plusieurs années.

## Décision

Auto-héberger **Traccar** (Apache 2.0) comme moteur d'ingestion et de positionnement temps réel. Traccar supporte 200+ protocoles / 2000+ modèles. Nous le traitons comme un **fournisseur de télémétrie remplaçable**, sans y mettre de logique métier.

## Alternatives écartées

- **Réécrire nos propres décodeurs** : effort énorme, réinvente Traccar, risque très élevé. ❌
- **Forker et absorber Traccar** : maîtrise totale mais charge de maintenance Java. Réévaluable plus tard. 🟡
- **Rester sur GPS-Trace** : contredit l'objectif d'indépendance. ❌

## Conséquences

- ✅ Indépendance immédiate, open source, usage commercial libre, zéro royalties.
- ✅ Time-to-market drastiquement réduit (mois vs années).
- ⚠️ Un composant Java à exploiter (Docker). Acceptable car isolé derrière un contrat API/WS.
- ⚠️ Intégration via API REST + WebSocket à construire (contexte `integrations`).
