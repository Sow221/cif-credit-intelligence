# CIF Credit Intelligence

Système de décision et de suivi du risque de crédit pour les institutions
financières — **Standard Production Élite**.

## Vue d'ensemble

- **Modèle** : XGBoost (25 features), PD = probabilité de défaut (classe 1).
- **Feature Service** : transforme le payload client (bruts + historiques) en
  25 features. Les Thin-File sont signalés (jamais de zéros artificiels).
- **Decision Engine** : PD + confiance + Thin-File → APPROBATION / REVUE_HUMAINE
  / AJUSTEMENT / REFUS.

## Stack

- Backend : FastAPI (Python 3.11)
- Frontend : React 18 + TypeScript + Vite
- ML : XGBoost, MLflow, Evidently
- Infra : Docker, Kubernetes, GitHub Actions

## Démarrage

```bash
make install
make backend-dev
make frontend-dev
```

## Tests

```bash
make test-backend   # pytest >= 90% de couverture
make test-frontend  # Vitest >= 80%
```

## Branches

- `main` : version stable
- `develop` : intégration continue (branche de travail par défaut)

## Documentation

Voir `docs/` (ADR, model card) et l'API Swagger à `/docs`.
