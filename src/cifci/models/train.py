"""Splits temporels et entraînement du modèle de scoring.

Implémente le contrat de validation CIF : split TOUJOURS temporel (jamais
aléatoire), XGBoost, calibration isotonique, et enregistrement d'un artefact
de modèle au même format que ``MODEL_OFFICIAL_CALIBRATED.joblib``.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import IsotonicRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from xgboost import XGBClassifier

from cifci.config import PROJECT_ROOT, get_config


def temporal_split(
    df: pd.DataFrame,
    *,
    order_col: str = "customer_id",
    split_date: float = 0.8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split temporel (protocole CIF) : l'ordre des lignes est l'ordre du temps.

    NB: le jeude données synthétique ne porte pas de vraie date. Le split
    temporel est représenté par l'ordre des ``customer_id`` (les premiers
    contrats sont les plus anciens). À substituer par une vraie colonne
    ``application_date`` lorsque les données CIF réelles arriveront.
    """
    df = df.sort_values(order_col).reset_index(drop=True)
    cutoff = int(len(df) * split_date)
    return df.iloc[:cutoff].copy(), df.iloc[cutoff:].copy()


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    *,
    params: dict | None = None,
    seed: int | None = None,
) -> XGBClassifier:
    """Entraîne un ``XGBClassifier`` sur le split d'entraînement.

    L'early stopping est appliqué sur le split de validation pour éviter le
    sur-apprentissage et choisir le bon nombre d'arbres.
    """
    cfg = get_config()
    mdl = cfg.model
    hp = params or {}
    seed = mdl.random_state if seed is None else seed

    model = XGBClassifier(
        n_estimators=hp.get("n_estimators", mdl.n_estimators),
        max_depth=hp.get("max_depth", mdl.max_depth),
        learning_rate=hp.get("learning_rate", mdl.learning_rate),
        subsample=hp.get("subsample", mdl.subsample),
        colsample_bytree=hp.get("colsample_bytree", mdl.colsample_bytree),
        objective=hp.get("objective", mdl.objective),
        eval_metric=hp.get("eval_metric", mdl.eval_metric),
        random_state=seed,
        n_jobs=-1,
        early_stopping_rounds=hp.get(
            "early_stopping_rounds", mdl.early_stopping_rounds
        ),
    )
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    return model


def calibrate(model: XGBClassifier, X_val: pd.DataFrame, y_val: pd.Series):
    """Calibre les probabilités avec IsotonicRegression sur la validation."""
    proba = model.predict_proba(X_val)[:, 1]
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(proba, y_val)
    return iso


def predict_proba(model, calibrator, X: pd.DataFrame) -> np.ndarray:
    """Probabilité calibrée de défaut pour ``X``."""
    raw = model.predict_proba(X)[:, 1]
    return np.clip(calibrator.predict(raw), 0.0, 1.0)


def evaluate_model(model, calibrator, X: pd.DataFrame, y: pd.Series) -> dict:
    """Calcule les métriques clés (avant/après calibration)."""
    probs = model.predict_proba(X)[:, 1]
    calib = np.clip(calibrator.predict(probs), 0.0, 1.0)
    y = y.to_numpy()
    return {
        "roc_auc_before": roc_auc_score(y, probs),
        "pr_auc_before": average_precision_score(y, probs),
        "brier_before": brier_score_loss(y, probs),
        "log_loss_before": log_loss(y, probs),
        "roc_auc_after": roc_auc_score(y, calib),
        "pr_auc_after": average_precision_score(y, calib),
        "brier_after": brier_score_loss(y, calib),
        "log_loss_after": log_loss(y, calib),
    }


def train_pipeline(
    customers: pd.DataFrame,
    loans: pd.DataFrame,
    *,
    out_path: Path | None = None,
) -> dict:
    """Pipeline d'entraînement complet (split temporel → modèle calibré).

    Returns:
        dict with keys ``model``, ``calibrator``, ``model_features``,
        ``calibration_method``, ``metrics_before``, ``metrics_after`` —
        format compatible avec ``MODEL_OFFICIAL_CALIBRATED.joblib``.
    """
    cfg = get_config()
    from cifci.features.build import prepare_feature_matrix

    X, y = prepare_feature_matrix(customers, loans)
    df = X.copy()
    df["__target__"] = y
    df["customer_id"] = customers["customer_id"].to_numpy()

    Xtr, Xval = temporal_split(df)
    ytr = Xtr["__target__"]
    yval = Xval["__target__"]
    Xtr = Xtr.drop(columns=["__target__", "customer_id"])
    Xval = Xval.drop(columns=["__target__", "customer_id"])

    model = train_model(Xtr, ytr, Xval, yval)
    calibrator = calibrate(model, Xval, yval)
    metrics_before, metrics_after = _split_metrics(
        evaluate_model(model, calibrator, Xval, yval)
    )

    artifact = {
        "model": model,
        "calibrator": calibrator,
        "model_features": list(cfg.features["list"]),
        "calibration_method": cfg.calibration.method,
        "metrics_before": metrics_before,
        "metrics_after": metrics_after,
    }

    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(artifact, out_path)

    return artifact


def _split_metrics(metrics: dict) -> tuple[dict, dict]:
    before = {k.replace("_before", ""): v for k, v in metrics.items() if "_before" in k}
    after = {k.replace("_after", ""): v for k, v in metrics.items() if "_after" in k}
    return before, after


def main() -> None:
    """CLI: entraîne le modèle sur data/raw et sauvegarde l'artefact."""
    from cifci.data.ingest import load_customers, load_loans

    customers = load_customers()
    loans = load_loans()

    out = (
        PROJECT_ROOT
        / "models"
        / "trained"
        / "reproduced_model.joblib"
    )
    artifact = train_pipeline(customers, loans, out_path=out)
    print("Entraînement terminé. Artefact :", out)
    print("Métriques (validation) :")
    print("  AVANT calibration :", artifact["metrics_before"])
    print("  APRÈS calibration :", artifact["metrics_after"])
