# Model Card — XGBoost v1 (`MODEL_OFFICIAL`)

**Version du modèle :** `MODEL_OFFICIAL` (calibré : `MODEL_OFFICIAL_CALIBRATED`)
**Date :** 2026-08-31
**Statut :** Production (registered)

## 1. Usage prévu
Classification binaire du risque de défaut de crédit : la probabilité de
défaut (PD) d'un client CIF, utilisée par le `Predictor` du backend pour
produire la recommandation de décision (APPROBATION / REVUE_HUMAINE /
AJUSTEMENT / REFUS).

## 2. Framework & données
- **Algorithme :** XGBoost Classifier.
- **Library :** `xgboost==3.2.0`.
- **Interface :** le modèle expose `feature_names_in_` = **25 features**,
  dans l'ordre exact du `FeatureRegistry`.
- **Jeu :** générateur synthétique (Phases A–D du Dossier) ; pipeline
  d'entraînement reproductible : `mlops/training/train_pipeline.py`.

## 3. Les 25 features (ordre du modèle)

| # | Feature | Type |
|---|---------|------|
| 1 | age | RAW |
| 2 | seniority_months | RAW |
| 3 | monthly_income | RAW |
| 4 | current_savings | RAW |
| 5 | avg_savings_24m | AGR |
| 6 | savings_std_24m | AGR |
| 7 | savings_volatility | AGR |
| 8 | savings_stability | AGR |
| 9 | n_past_loans | RAW |
| 10 | current_loan_request | RAW |
| 11 | current_loan_duration | RAW |
| 12 | loan_to_savings_ratio | DERIVED |
| 13 | n_loans | AGR |
| 14 | avg_loan_amount | AGR |
| 15 | total_loan_amount | AGR |
| 16 | avg_repayment_regularity | AGR |
| 17 | min_repayment_regularity | AGR |
| 18 | max_historical_dpd | AGR |
| 19 | mean_historical_dpd | AGR |
| 20 | n_defaults | AGR |
| 21 | loan_to_income_ratio | DERIVED |
| 22 | historical_default_rate | DERIVED |
| 23 | savings_to_income_ratio | DERIVED |
| 24 | seniority_years | DERIVED |
| 25 | overall_payment_regularity | DERIVED |

(RAW = directe, DERIVED = calculée, AGR = agrégation d'historique.)

## 4. Métriques de performance
Enregistrées à chaque run via MLflow (`mlops/training/train_pipeline.py`).
À renseigner depuis la registration en production :

| Métrique | Valeur (à confirmer par MLflow) |
|----------|---------------------------------|
| ROC AUC | _à enregistrer_ |
| PR AUC | _à enregistrer_ |
| Brier Score | _à enregistrer_ |
| Precision / Recall | _à enregistrer_ |

> Ces métriques sont tracées dans `model_versions` (table SQL) lors de la
> promotion du modèle.

## 5. Règles de décision (DecisionEngine)
| Règle | Condition | Décision |
|-------|-----------|----------|
| R1 | confiance FAIBLE | REVUE_HUMAINE |
| R2 | Thin-File (`n_past_loans == 0` / `has_history=false`) | REVUE_HUMAINE |
| R3 | PD ≤ 0.10 | APPROBATION |
| R4 | 0.10 < PD ≤ 0.25 | REVUE_HUMAINE |
| R5 | 0.25 < PD ≤ 0.45 | AJUSTEMENT |
| R6 | PD > 0.45 | REFUS |

## 6. Biais / équité & limites
- **Thin-File :** jamais de zéros artificiels ; renvoi en revue humaine sans
  appel au modèle.
- **Limite :** jeu d'entraînement synthétique ; le drift est surveillé par
  Evidently (`mlops/monitoring`) avant toute montée en charge réelle.

## 7. Cycle de vie
- Artefact non versionné : `mlops/artifacts/MODEL_OFFICIAL.joblib`
  (`.gitignore`), restauré via S3 / secret CI.
- Nouvelles versions : `mlops/training/train_pipeline.py` + MLflow ;
  promotion via `model_versions`.
