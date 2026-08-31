# CIF Credit Intelligence

Système de décision et de suivi du risque de crédit pour les institutions
financières — **Standard Production Élite**.

`backend/` API de prédiction de défaut · `frontend/` interface agent/superviseur
· `mlops/` entraînement et monitoring · `infrastructure/` déploiement AWS.

---

## Architecture

```
cif-credit-intelligence/
├─ backend/            # API FastAPI (Python 3.11)
│  └─ src/
│     ├─ api/          # routes (/v1), middlewares (JWT, request-id, rate limit)
│     ├─ services/     # predictor, decision_engine, confidence, audit, features
│     ├─ features/     # registre des 25 features
│     ├─ models/       # interface XGBoost (.joblib)
│     ├─ db/ + migrations/   # SQLAlchemy + Alembic (PostgreSQL)
│     └─ config/       # Pydantic Settings
├─ frontend/           # React 18 + TypeScript strict + Vite + Tailwind (nginx)
├─ mlops/              # artifacts (non versionnés), training, monitoring (Evidently, MLflow)
├─ infrastructure/
│  ├─ docker/          # docker-compose.yml (+ prod, nginx.conf)
│  ├─ k8s/             # manifestes Kubernetes (agnostiques)
│  └─ terraform/       # provisionnement AWS (EC2, RDS, S3, ECR)
├─ docs/               # ADR, model card, documentation API
└─ .github/workflows/  # backend-ci, frontend-ci, deploy
```

## Fonctionnement

- **25 features** transformées depuis le payload client (champs bruts +
  historique épargne / prêts) par le `FeatureService`.
- **Thin-File** : jamais de zéros artificiels — décision `REVUE_HUMAINE`
  sans appel au modèle.
- **Decision Engine** : PD + confiance + Thin-File → APPROBATION /
  REVUE_HUMAINE / AJUSTEMENT / REFUS (règles R1–R6).
- **Persistance** : prédictions, décisions/overrides, audit et versions de
  modèle dans PostgreSQL (tracabilité réglementaire).

## Démarrage (local)

```bash
make install            # backend (pip -e .[dev]) + frontend (npm install) + pre-commit

# Base de données PostgreSQL (Docker, port 5440)
make db-up
make migrate            # alembic upgrade head

# Artefacts ML (depuis le dépôt source local)
make artifacts-init

make backend-dev        # uvicorn http://localhost:8000  (Swagger : /docs)
make frontend-dev       # Vite http://localhost:5173
```

## Tests & quality gates

```bash
make test-backend       # pytest --cov >= 90 %
make test-frontend      # Vitest
make lint               # black / ruff / mypy (backend) + eslint (frontend)
```

État : **38 tests backend** + **9 tests frontend** verts.

## Déploiement (production — AWS Free Tier)

Décision `reponse.txt` : Terraform `hashicorp/aws` (EC2 t2.micro, RDS
PostgreSQL 15, S3, ECR). Manifestes k8s conservés agnostiques.

```bash
cd infrastructure/terraform
terraform init && terraform plan && terraform apply
# Outputs : IP EC2, endpoint RDS, bucket S3, URIs ECR

# Sur le serveur (SSH) :
docker compose -f infrastructure/docker/docker-compose.prod.yml up -d --build
```

CI/CD : `.github/workflows/` (backend-ci, frontend-ci, deploy).

> Le modèle ML n'est **pas versionné** (`.gitignore`). Il est restauré en CI
> depuis le secret `ARTIFACTS_BASE64` ou S3. Voir `mlops/scripts/init_artifacts.py`.

## Branches

- `main` : version stable
- `develop` : intégration continue (branche de travail par défaut)

## Documentation

- `docs/adr/` — décisions d'architecture (001–004)
- `docs/model_cards/xgboost_v1.md` — carte du modèle
- `docs/api_documentation.md` — contrat des 11 endpoints
- Swagger de l'API : `/docs`
