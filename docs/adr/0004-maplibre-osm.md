# ADR 0004 — Cartographie MapLibre GL + OpenStreetMap

- **Statut** : Accepté
- **Date** : 2026-06-09

## Contexte

La plateforme a besoin de cartes (suivi temps réel, trajets, géofences). Le choix du fournisseur cartographique a un impact sur le coût, la dépendance et le contrôle.

## Décision

Utiliser **MapLibre GL JS** (rendu vectoriel open source) avec des tuiles **OpenStreetMap** (fournisseur de tuiles tiers gratuit/à faible coût, ou tuiles auto-hébergées).

## Justification

- **Cohérent avec l'objectif d'indépendance** : pas de verrou Google, pas de facturation à l'usage imprévisible.
- MapLibre est un fork open source de Mapbox GL, performant et activement maintenu.
- OpenStreetMap : couverture mondiale, données ouvertes, bonne couverture Afrique.
- Possibilité d'**auto-héberger les tuiles** (TileServer GL) pour une indépendance totale.

## Alternatives écartées

- **Google Maps** : qualité élevée mais coût à l'usage + verrou + clé API. ❌
- **Mapbox** : excellent mais payant au-delà d'un quota + verrou. 🟡

## Conséquences

- ✅ Indépendance, coût maîtrisé, possibilité d'auto-hébergement.
- ⚠️ Qualité des tuiles OSM variable selon les régions ; mitigable par un fournisseur de tuiles dédié.
