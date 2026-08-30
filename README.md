<div align="center">

# 💳 CIF Credit Intelligence

**Système de décision et de suivi du risque de crédit pour les institutions financières**  
*Standard Production Élite*

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML-EC9A29?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-brightgreen?style=flat-square)](#)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Coverage](https://img.shields.io/badge/Coverage-%E2%89%A590%25-brightgreen?style=flat-square)](#)

</div>

---

## 📌 Vue d'ensemble

* **🤖 Modèle ML** : XGBoost (ex : 20–30 features) prédisant la probabilité de défaut (PD).  
* **⚡ Feature Service** : Transformations reproductibles du payload client (données brutes & historiques). Traitement dédié des *thin-files* sans injection de zéros artificiels.  
* **🎯 Decision Engine** : Combinaison PD + Confiance + Thin-File → décisions : `APPROBATION`, `REVUE_HUMAINE`, `AJUSTEMENT`, `REFUS`.  
* **♻️ MLOps** : Enregistrement des modèles et métriques (MLflow), monitoring de performances & drift (Evidently).

---

## 🛠️ Stack Technique (exemple)

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| 🖥️ **Backend** | Python 3.11, FastAPI | API & Feature Service |
| 🤖 **Machine Learning** | XGBoost, scikit-learn, MLflow | Modélisation & tracking |
| 📊 **Monitoring** | Evidently, Prometheus, Grafana | Drift & data quality |
| 🧩 **Infra** | Docker, GitHub Actions | Conteneurisation & CI |
| ✅ **Tests** | pytest, coverage | Qualité, tests unitaires & intégration |

---

## 🚀 Démarrage rapide

1) Cloner le dépôt
```bash
git clone https://github.com/Sow221/cif-credit-intelligence.git
cd cif-credit-intelligence
```

2) Installation (utilise le Makefile présent)
```bash
# créer venv + installer dépendances
make install
```

3) Lancer en dev
```bash
# backend en mode développement (FastAPI + hot reload)
make backend-dev
```

4) Tests
```bash
# Tests backend (objectif couverture >= 90%)
make test-backend
```

---

## 🧪 Qualité & Tests

- Couverture minimale souhaitée : Backend >= 90%.  
- Tests d'intégration pour le Feature Service et le Decision Engine.  
- Linting & format : black, isort, ruff.

---

## 🌿 Stratégie de branches

- `main` : production stable.  
- `develop` : intégration continue / pré-prod.  
- Feature branches : `feature/<ticket>-desc`.

---

## 📚 Documentation

- docs/ — ADRs, Model Card, schémas d'API et guide d'intégration.  
- API interactive : /docs (Swagger UI) lorsqu'elle est lancée localement.

---

## ✅ Checklist pour atteindre le niveau "Top Level / Élite"

- [ ] README riche + badges fonctionnels (coverage, license, CI).  
- [ ] Model Card complète (dataset, features, performance, fairness).  
- [ ] ADRs pour décisions d'architecture critiques.  
- [ ] Tests unitaires & d'intégration avec seuils de coverage.  
- [ ] CI enforcement (checks qui bloquent merges si couverture insuffisante).  
- [ ] Dockerfile multi-stage + Compose / Helm chart pour déploiement.  
- [ ] Observabilité (logs structurés, traces, métriques & alerting).

---

## ✍️ Personnalisation

Les sections ci‑dessus contiennent des placeholders (ex. XGBoost, FastAPI). Dites-moi si vous voulez que j'adapte le README à l'état exact du repo (par ex. remplacer FastAPI par Flask, ajouter les badges CI/coverage réels, lister les dépendances clés à partir du fichier requirements.txt).
