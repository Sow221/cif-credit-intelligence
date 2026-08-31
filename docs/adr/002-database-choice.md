# ADR-002 : Choix de la base de données

**Statut :** Accepté
**Date :** 2026-08-31
**Contexte :** Le système a besoin de persister les prédictions, les
décisions/overrides, le journal d'audit et les versions de modèle, avec une
contrainte de traçabilité réglementaire.

## Décision
Utiliser **PostgreSQL 15** (via Docker en local, RDS managé en production),
avec :

- **SQLAlchemy 2.0** comme ORM.
- **psycopg v3** comme driver (psycopg2 était défaillant sur Windows).
- **Alembic** pour les migrations versionnées.
- 4 tables : `customers`, `predictions`, `audit_log`, `model_versions`
  (Dossier : Partie 4), UUID natif PG pour les clés primaires.
- Index sur `customer_id` et `created_at` (performance des listes).

## Alternatives considérées
- **SQLite** : non adapté à la concurrence et au volume en production.
- **MongoDB** : schéma libre, mais le contrat SQL/0RM et la traçabilité
  exigent un relationnel transactionnel.

## Conséquences
- `/v1/predict` persiste les prédictions (upsert client) — ce qui alimente
  `/v1/decisions` et `/v1/audit`.
- Migration initiale `001_initial.py` appliquée (4 tables).
- Parité base locale (Docker, port 5440) / production (RDS).
