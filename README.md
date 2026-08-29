# CIF Credit Intelligence

**Infrastructure d'intelligence de crédit et de décision de risque** pour les
institutions financières (SFD / microfinance) d'Afrique de l'Ouest. Le projet
combine un moteur de scoring (machine learning), un moteur de décision supervisée,
et un **protocole de validation rigoureux** conçu *avant* toute donnée réelle —
pour produire des décisions de financement contextualisées, explicables et
auditables.

> ⚠️ **Statut méthodologique** : la phase **synthétique** est clôturée et a servi
> d'environnement de validation méthodologique. Le `ROC-AUC ≈ 0.83` est un
> résultat **expérimental sur données synthétiques**, ce **n'est pas un benchmark
> CIF**. La performance réelle ne pourra être évaluée que sur les données CIF
> anonymisées, via le protocole de validation locké dans `docs/`.

---

## Table des matières

- [Pourquoi ce projet](#pourquoi-ce-projet)
- [Ce que fait la solution](#ce-que-fait-la-solution)
- [Le point différenciant : la méthode](#le-point-diff%C3%A9renciant--la-m%C3%A9thode)
- [Architecture du dépôt](#architecture-du-d%C3%A9p%C3%B4t)
- [Quickstart](#quickstart)
- [Stack technique](#stack-technique)
- [Résultats synthétiques](#r%C3%A9sultats-synth%C3%A9tiques)
- [Limites & frontière méthodologique](#limites--fronti%C3%A8re-m%C3%A9thodologique)
- [Gouvernance & conformité](#gouvernance--conformit%C3%A9)
- [Roadmap](#roadmap)

---

## Pourquoi ce projet

Les institutions de microfinance de l'UEMOA disposent de **données réelles mais
fragmentées** (crédit, épargne, remboursements). Transformer ces données en
décisions de financement **fiables** exige plus qu'un modèle de ML : il faut une
chaîne de validation capable de prouver l'absence de fuite d'information
(leakage), la stabilité temporelle, l'équité entre groupes et la rentabilité
d'une supervision humaine.

Ce projet formalise cette chaîne, du **jeu de données synthétique calibré**
jusqu'à un **protocole verrouillé pour la phase réelle**.

## Ce que fait la solution

1. **Moteur de scoring** : probabilité de défaut estimée par XGBoost sur
   25 caractéristiques (profil, épargne, historique de remboursement),
   recalibrée par régression **isotonique** (les probabilités sorties sont
   *fiables*, pas seulement *bien classées*).
2. **Moteur de décision** : à partir de la probabilité et du profil
   (notamment les *thin-file*), oriente vers 4 décisions :
   `APPROBATION`, `REVUE_HUMAINE`, `AJUSTEMENT`, `REFUS`.
3. **Pilotage économique** : fonction de coût (revue, faux positifs, faux
   négatifs) pour choisir le seuil et la capacité de revue humaine optimaux.
4. **Explicabilité** : chaîne `DATA → INTELLIGENCE → RISK → DECISION`,
   avec importance globale et contributions **SHAP** locales par client
   (exposées via l'API).

## Le point différenciant : la méthode

La valeur n'est pas le score, c'est **la discipline de validation lockée avant
les données** (cf. `docs/`). Les protocoles suivants sont gelés pour la phase
réelle :

| Protocole | Fichier | Contenu |
|---|---|---|
| Protocole de validation CIF | `docs/03_protocole_validation_cif_*.json` | Split temporel, IC95 bootstrap, segments, fairness, GO/NO-GO |
| Template Data Audit | `docs/CIF_DATA_AUDIT_V1.1_*.json` | Audit population/temporalité/cible/qualité/biais |
| Readiness pack | `docs/CIF_REAL_DATA_READINESS_PACK_*.json` | Intake, validation stat., leakage, gate, registry de décision |

**Garanties imposées** : split **temporel** (jamais aléatoire), exclusion de
toute variable **post-décision**, IC95 sur **chaque** métrique et **chaque**
groupe, thin-file segmentés, coûts réels pour les seuils.

## Architecture du dépôt

```
.
├── src/cifci/          # Package principal (source de vérité)
│   ├── data/          #   ingestion / génération synthétique seedée
│   ├── features/      #   feature engineering + GARDE ANTI-LEAKAGE
│   ├── models/        #   entraînement, calibration, registre
│   ├── evaluate/      #   métriques, bootstrap CI, segments CIF
│   ├── decision/      #   moteur de décision
│   ├── explain/       #   explicabilité (SHAP local + global)
│   ├── pipeline/      #   étapes CLI appelées par DVC
│   └── api/           #   service de scoring (FastAPI) + CLI
├── tests/             # pytest : anti-leakage, temporalité, features, API
├── configs/params.yaml# Tous les paramètres centralisés (source de vérité)
├── dvc.yaml           # Pipeline reproductible (prepare → train → evaluate)
├── data/              # Données (DVC-tracked, hors git)
├── models/            # Modèles & registre (DVC-tracked, hors git)
├── reports/           # Audits A-F, figures, métriques (versionnées)
├── docs/              # Protocoles & documentation de validation
├── .github/workflows/ # CI : ruff, mypy, pytest, garde anti-leakage
└── dashboard/         # (à venir) interface de suivi
```

## Quickstart

```bash
# 1. Installer uv (gestionnaire d'environnements)
#    https://docs.astral.sh/uv/

# 2. Installer les dépendances et le package (mode édit)
uv sync --extra dev --extra test

# 3. Vérifier la santé : le garde anti-leakage doit être VERT
uv run pytest tests/ -q

# 4. Lancer la pipeline complète (reproductible — DVC)
uv run dvc repro          # prepare → train → evaluate

# 5. (Optionnel) Lancer l'API de scoring en local
uv run uvicorn cifci.api.app:app --reload   # → http://127.0.0.1:8000/docs
```

> [!NOTE] **Industrialisation livrée** : pipeline DVC rejouable, CI/CD
> (GitHub Actions : ruff, mypy, pytest, garde anti-leakage), API FastAPI
> (`/score`, `/explain`, `/health`), CLI de prédiction, SHAP et pre-commit.
> Chaque étape est versionnée et testable — rien de jetable.

## Stack technique

- **Langage** : Python 3.11
- **ML** : scikit-learn, XGBoost
- **Calibration** : régression isotonique (IC`sklearn`)
- **Validation** : bootstrap stratifié, IC95, PSI, ablation, multi-seed
- **Suivi / registre** : MLflow (Tracking + Model Registry)
- **API** : FastAPI + Uvicorn
- **Qualité** : pytest, ruff, mypy, pre-commit (CI GitHub Actions)
- **Versioning données/modèles** : DVC

## Résultats synthétiques

> Ces chiffres sont **expérimentaux** sur données synthétiques calibrées
> (taux de défaut cible ≈ 11.8%, seed contrôlé). À ne JAMAIS présenter comme
> une performance réelle.

| Métrique | Modèle officiel (synthétique) | Pipeline reproduit (DVC) |
|---|---|---|
| ROC-AUC | ≈ 0.83 | ≈ 0.87 |
| PR-AUC | ≈ 0.47 | ≈ 0.49 |
| Brier (après calibration) | ≈ 0.084 | ≈ 0.075 |
| IC95 bootstrap (ROC-AUC) | — | [0.86, 0.88] |
| Segmentation thin-file / riche | validée | thin-file 0.82 → historique 4+ 0.85 |

Le pipeline reproduit les métriques du modèle officiel **à partir du code**
(`dvc repro`), avec un léger gain lié à la reconstruction propre des features.

Audits menés (`reports/audit/`) : multi-seed, sans-signal, facteur latent,
bootstrap, robustesse, drift, fairness, matrice de généralisation
(`A_to_B ≈ 0.57` → généralisation **partielle**, loyalement documentée),
fonction de coût et capacité de revue.

## Limites & frontière méthodologique

- **Données synthétiques ≠ données CIF réelles.** Aucun chiffre ici ne se
  substitue à un benchmark sur données réelles.
- **Généralisation partielle** mesurée entre générateurs de données : ~25 % de
  la performance est spécifique au générateur d'entraînement → le niveau
  réaliste sur données hors-échantillon est bien plus bas que 0.83.
- **Seuils du décision engine PROVISOIRES** : à recalculer avec target, coûts
  et capacité réels de la CIF.
- Ce qui **ne doit pas être inventé** : définition CIF du défaut, variables
  disponibles, période couverte, taux de défaut réel, seuils définitifs.

## Gouvernance & conformité

Alignement intentionnel avec les exigences d'un environnement réglementé
(BCEAO / SFD) :
- **Split temporel** et exclusion des variables post-décision (anti-leakage
  formel, test en CI).
- **Équité** analysée par groupe (genre, secteur, zone) avec IC95 ; petits
  groupes marqués « estimation instable » plutôt que cachés.
- **Traçabilité** : registre de modèles + journal de bord des décisions
  (`journal_bord.json`).
- **Supervision humaine** : le système n'automatise que ce qui est
  statistiquement et économiquement justifié (revue optimale ≈ 590/2000).

## Roadmap

- [x] **Industrialisation** : pipeline DVC rejouable (`make`/`dvc repro`),
  CI/CD GitHub Actions (ruff, mypy, pytest, anti-leakage), API FastAPI
  conteneurisable, CLI de prédiction, SHAP local/global, pre-commit.
- [ ] **Phase réelle CIF** : recevoir un échantillon anonymisé → exécuter
  `CIF_DATA_AUDIT_V1.1` → GO/NO-GO.
- [ ] **Extension produit** : early-warning, portfolio intelligence,
  interopérabilité (TELQAN Connect), monitoring (drift/performance),
  Model Card & Data Card, dashboard de suivi.

---

*Projet personnel — spécialisation IA & données appliquée à la finance.
Phase synthétique clôturée : `READY FOR REAL-DATA AUDIT`.*
