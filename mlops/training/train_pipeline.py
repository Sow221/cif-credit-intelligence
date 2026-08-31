"""Pipeline d'entrainement du modele XGBoost CIF.

Produit `MODEL_OFFICIAL.joblib` dans `mlops/artifacts/` (les 25 features
exactes du registre), journalise le run dans MLflow, enregistre le modele
dans le Registry (`microcredit_risk/Production`) et logge les metriques
dans Weights & Biases (optionnel).

Usage :
    python mlops/training/train_pipeline.py [--data chemin.csv] [--experiment cif]
    python mlops/training/train_pipeline.py --no-mlflow --no-wandb

Si `--data` est absent, un jeu synthetique documente est genere (meme
contrat de 25 features) pour valider le pipeline de bout en bout.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Chemin projet = racine du repo
ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / "mlops" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "MODEL_OFFICIAL.joblib"

# Nom du modele dans le Registry MLflow (stack validee).
REGISTRY_NAME = "microcredit_risk"
REGISTRY_ALIAS = "Production"

# 25 features exactes (ordre du registre officiel).
FEATURES = [
    "age",
    "seniority_months",
    "monthly_income",
    "current_savings",
    "avg_savings_24m",
    "savings_std_24m",
    "savings_volatility",
    "savings_stability",
    "n_past_loans",
    "current_loan_request",
    "current_loan_duration",
    "loan_to_savings_ratio",
    "n_loans",
    "avg_loan_amount",
    "total_loan_amount",
    "avg_repayment_regularity",
    "min_repayment_regularity",
    "max_historical_dpd",
    "mean_historical_dpd",
    "n_defaults",
    "loan_to_income_ratio",
    "historical_default_rate",
    "savings_to_income_ratio",
    "seniority_years",
    "overall_payment_regularity",
]


def generate_synthetic(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Genere un jeu synthetique respectant le contrat des 25 features."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame()

    df["age"] = rng.integers(18, 65, n).astype(float)
    df["seniority_months"] = rng.integers(0, 60, n).astype(float)
    df["monthly_income"] = rng.uniform(200, 5000, n)
    df["current_savings"] = rng.uniform(0, 20000, n)
    df["avg_savings_24m"] = df["current_savings"] * rng.uniform(0.7, 1.1, n)
    df["savings_std_24m"] = rng.uniform(0, df["current_savings"] / 2, n)
    df["savings_volatility"] = df["savings_std_24m"] / (df["avg_savings_24m"] + 1)
    df["savings_stability"] = np.clip(0.5 + rng.uniform(-0.5, 0.5, n) * 0.35, 0.05, 0.95)
    df["n_past_loans"] = rng.integers(0, 10, n).astype(float)
    df["current_loan_request"] = rng.uniform(100, 15000, n)
    df["current_loan_duration"] = rng.integers(1, 60, n).astype(float)
    df["loan_to_savings_ratio"] = df["current_loan_request"] / (df["current_savings"] + 1)
    df["n_loans"] = df["n_past_loans"]
    df["avg_loan_amount"] = rng.uniform(200, 8000, n)
    df["total_loan_amount"] = df["avg_loan_amount"] * np.maximum(df["n_loans"], 1)
    df["avg_repayment_regularity"] = rng.uniform(0.5, 1.0, n)
    df["min_repayment_regularity"] = df["avg_repayment_regularity"] * rng.uniform(0.6, 1.0, n)
    df["max_historical_dpd"] = rng.integers(0, 90, n).astype(float)
    df["mean_historical_dpd"] = df["max_historical_dpd"] * rng.uniform(0.2, 0.9, n)
    df["n_defaults"] = rng.binomial(1, 0.2, n).astype(float)
    df["loan_to_income_ratio"] = df["current_loan_request"] / (df["monthly_income"] + 1)
    df["historical_default_rate"] = df["n_defaults"] / (df["n_loans"] + 1)
    df["savings_to_income_ratio"] = df["current_savings"] / (df["monthly_income"] + 1)
    df["seniority_years"] = df["seniority_months"] / 12

    # Regularite globale : moyenne ponderee par le nombre de prets
    df["overall_payment_regularity"] = (
        df["n_loans"] * df["avg_repayment_regularity"] / (df["n_loans"] + 1)
    )

    # Cible : risque augmente avec le ratio d'endettement et les retards
    risk = (
        0.15 * df["loan_to_income_ratio"]
        + 0.3 * df["max_historical_dpd"] / 90
        + 0.3 * df["historical_default_rate"]
        + 0.2 * df["n_defaults"] / 5
    )
    df["default"] = (risk > rng.uniform(0.35, 0.5)).astype(int)

    return df[FEATURES + ["default"]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Entrainement XGBoost CIF")
    parser.add_argument("--data", type=str, default=None, help="CSV d'entrainement (optionnel)")
    parser.add_argument("--experiment", type=str, default="cif-credit")
    parser.add_argument("--registry-name", type=str, default=REGISTRY_NAME,
                        help="Nom du modele dans le Registry MLflow")
    parser.add_argument("--alias", type=str, default=REGISTRY_ALIAS,
                        help="Alias a attribuer dans le Registry")
    parser.add_argument("--mlflow-uri", type=str, default="http://localhost:5001",
                        help="URI du serveur MLflow")
    parser.add_argument("--no-mlflow", action="store_true", help="Desactiver MLflow")
    parser.add_argument("--no-wandb", action="store_true", help="Desactiver W&B")
    args = parser.parse_args()

    if args.data:
        df = pd.read_csv(args.data)
        target = "default"
    else:
        print("[info] Aucun --data fourni, generation du jeu synthetique.")
        df = generate_synthetic()
        target = "default"

    if set(FEATURES).issubset(df.columns) and target in df.columns:
        X = df[FEATURES].astype(float)
        y = df[target].astype(int)
    else:
        print("[error] Le jeu de donnees ne respecte pas le contrat des 25 features.", file=sys.stderr)
        return 1

    train_cut = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:train_cut], X.iloc[train_cut:]
    y_train, y_test = y.iloc[:train_cut], y.iloc[train_cut:]

    import xgboost as xgb
    from sklearn.metrics import (
        accuracy_score,
        brier_score_loss,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    mlflow = None
    if not args.no_mlflow:
        try:
            import mlflow as _mlflow

            _mlflow.set_tracking_uri(args.mlflow_uri)
            _mlflow.set_experiment(args.experiment)
            mlflow = _mlflow
        except Exception as exc:  # noqa: BLE001 - MLflow optionnel
            print(f"[warn] MLflow indisponible : {exc}")
            mlflow = None

    wandb_run = None
    if not args.no_wandb:
        try:
            import wandb

            wandb_run = wandb.init(project="cif-credit-intelligence", job_type="train")
        except Exception as exc:  # noqa: BLE001 - W&B optionnel
            print(f"[warn] W&B indisponible : {exc}")
            wandb_run = None

    if mlflow is not None:
        mlflow.autolog()

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="auc",
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "pr_auc": float(roc_auc_score(y_test, y_proba)),
        "brier_score": float(brier_score_loss(y_test, y_proba)),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
    }

    if mlflow is not None:
        mlflow.log_metrics(metrics)
        mlflow.log_param("n_features", len(FEATURES))
        mlflow.log_param("registry_name", args.registry_name)
        mlflow.log_param("registry_alias", args.alias)

    if wandb_run is not None:
        wandb_run.log(metrics)
        wandb_run.log({"n_features": len(FEATURES)})

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    import joblib

    joblib.dump(model, MODEL_PATH)
    print("[ok] Modele enregistre :", MODEL_PATH)
    print("[metrics]", metrics)

    # Enregistrement dans le Registry MLflow (stack validee : models:/...).
    if mlflow is not None:
        try:
            from mlflow import MlflowClient
            from mlflow.models.signature import ModelSignature
            from mlflow.types.schema import ColSpec, Schema

            signature = ModelSignature(
                inputs=Schema([ColSpec("double", name=c) for c in FEATURES]),
                outputs=Schema([ColSpec("double"), ColSpec("double")]),
            )
            model_info = mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                registered_model_name=args.registry_name,
                signature=signature,
            )
            client = MlflowClient()
            versions = client.search_model_versions(
                f"name = '{args.registry_name}'"
            )
            for v in versions:
                client.set_registered_model_alias(
                    args.registry_name, args.alias, v.version
                )
            mlflow.log_param("registered_model_uri", model_info.model_uri)
            print("[ok] Modele enregistre dans le Registry :",
                  f"models:/{args.registry_name}@{args.alias}")
        except Exception as exc:  # noqa: BLE001 - enregistrement optionnel
            print(f"[warn] Enregistrement dans le Registry echoue : {exc}")

    if wandb_run is not None:
        wandb_run.finish()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
