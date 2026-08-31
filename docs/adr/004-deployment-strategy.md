# ADR-004 : Stratégie de déploiement

**Statut :** Accepté
**Date :** 2026-08-31
**Contexte :** Le système doit être déployé en production avec une
infrastructure reproductible, un monitoring et un coût maîtrisé.

## Décision
Cibler **AWS Free Tier** (décision `reponse.txt`) avec une approche en
couches, les manifestes Kubernetes restant **agnostiques** :

| Couche | Choix | Rôle |
|--------|-------|------|
| Provision | **Terraform (provider `hashicorp/aws`)** | EC2, RDS, S3, ECR, security groups |
| Compute | **EC2 t2.micro** (Ubuntu 22.04, Docker) | API FastAPI, MLflow |
| Base de données | **RDS PostgreSQL 15** (db.t3.micro) | Persistent layer managée |
| Stockage | **S3** (bucket versionné) | Modèles `.joblib`, rapports de drift |
| Registre | **ECR** | Images `cif-backend`, `cif-frontend` |
| Monitoring | **CloudWatch** + Evidently | Métriques VM + data drift |
| Conteneurisation | **Docker / docker-compose** | Services `db`, `api`, `frontend`, `mlflow` |
| Orchestration (futur) | **Kubernetes** (manifestes agnostiques) | Passerelle quand 2+ nœuds |

## Cycle de vie
```
TERRAFORM (provisionne EC2 + RDS + S3)
      ↓
DOCKER COMPOSE (déploie api / frontend / mlflow + migration Alembic)
      ↓
CI/CD (build + push ECR ou GHCR)
      ↓
MONITORING (sondes /health/*, Evidently drift, CloudWatch)
      ↓
HTTPS (en-tête derrière proxy / domaine)
```

## Alternatives considérées
- **Hetzner + DuckDNS + Let's Encrypt** : retenu précédemment, abandonné au
  profit d'AWS Free Tier (décision la plus récente).
- **GCP / Azure** : équivalents, non retenus.

## Conséquences
- Le modèle ML n'est **pas versionné** ; il est livré via artefact (S3 /
  secret CI `ARTIFACTS_BASE64`) puis présent dans l'image ou monté.
- `terraform init/plan/apply` produit l'infra ; outputs exposés
  (IP EC2, endpoint RDS, bucket S3, URIs ECR).
- Sondes liveness/readiness branchées sur `/health/live` et `/health/ready`.
