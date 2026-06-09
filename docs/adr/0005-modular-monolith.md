# ADR 0005 — Monolithe modulaire

- **Statut** : Accepté
- **Date** : 2026-06-09

## Contexte

Projet mono-entreprise, équipe de taille modérée, besoin de livrer vite tout en gardant la porte ouverte à la montée en charge.

## Décision

Architecturer le backend en **monolithe modulaire** : un seul déploiement Django, mais découpé en **contextes délimités** (apps) avec des frontières nettes.

## Règles

- Chaque app (`accounts`, `fleet`, `telemetry`, `crm`, `billing`, `maintenance`, `geofencing`, `notifications`, `reporting`, `audit`, `integrations`) possède ses modèles, services, serializers, vues, urls.
- Communication inter-modules via une **couche service** explicite, pas d'import croisé de vues.
- Pas de dépendances circulaires entre apps.

## Justification

- Simplicité opérationnelle d'un monolithe (un déploiement, une base de transactions).
- Frontières claires → extraction ultérieure en microservice possible **sans réécriture**.
- Évite la complexité prématurée des microservices (réseau, cohérence distribuée).

## Alternatives écartées

- **Microservices d'emblée** : surcoût opérationnel injustifié à ce stade. ❌
- **Monolithe non structuré** : dette technique garantie (l'erreur de l'ancien DGMS à éviter). ❌

## Conséquences

- ✅ Vélocité + évolutivité.
- ⚠️ Discipline requise sur les frontières (revue de code, lint d'architecture).
