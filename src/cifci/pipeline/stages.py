"""CLI des étapes du pipeline DVC (préparation → entraînement → évaluation).

Chaque fonction correspond à une étape du ``dvc.yaml`` et peut être appelée
en ligne de commande pour une reproductibilité totale.
"""

from __future__ import annotations

import argparse
import json
import sys

from cifci.config import PROJECT_ROOT, get_config


def _prepare_features(argv: list[str] | None = None) -> int:
    """Étape 1 : génère le CSV de features préparées (anti-leakage inclus)."""
    parser = argparse.ArgumentParser(prog="cifci-prepare-features")
    parser.add_argument("--customers", required=True)
    parser.add_argument("--loans", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    import pandas as pd

    from cifci.features.build import build_features

    customers = pd.read_csv(args.customers)
    loans = pd.read_csv(args.loans)
    df = build_features(customers, loans)
    # La matrice préparée contient features + cible, sans jamais la fuite.
    df.to_csv(args.out, index=False)
    print(f"Features préparées écrites : {args.out} ({df.shape[0]} lignes, {df.shape[1]} colonnes)")
    return 0


def _train(argv: list[str] | None = None) -> int:
    """Étape 2 : entraîne le modèle calibré depuis le CSV de features."""
    parser = argparse.ArgumentParser(prog="cifci-apply-train")
    parser.add_argument("--features", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    import joblib
    import pandas as pd

    from cifci.features.validate import assert_no_leakage
    from cifci.models.train import calibrate, evaluate_model, temporal_split, train_model

    cfg = get_config()
    df = pd.read_csv(args.features)
    df = assert_no_leakage(
        df, feature_columns=list(cfg.features["list"]), allow_target=True
    )
    # Construction du split temporel et entraînement.
    df_sorted = df.sort_values("customer_id").reset_index(drop=True)
    cutoff = int(len(df_sorted) * 0.8)
    train_df = df_sorted.iloc[:cutoff].copy()
    val_df = df_sorted.iloc[cutoff:].copy()
    feats = list(cfg.features["list"])
    Xtr, ytr = train_df[feats], train_df["is_default"]
    Xval, yval = val_df[feats], val_df["is_default"]

    model = train_model(Xtr, ytr, Xval, yval)
    calibrator = calibrate(model, Xval, yval)
    metrics = evaluate_model(model, calibrator, Xval, yval)

    artifact = {
        "model": model,
        "calibrator": calibrator,
        "model_features": feats,
        "calibration_method": cfg.calibration.method,
        "metrics_before": {k.replace("_before", ""): v for k, v in metrics.items() if "_before" in k},
        "metrics_after": {k.replace("_after", ""): v for k, v in metrics.items() if "_after" in k},
    }
    import os

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    joblib.dump(artifact, args.out)
    print(f"Modèle entraîné et sauvegardé : {args.out}")
    return 0


def _evaluate(argv: list[str] | None = None) -> int:
    """Étape 3 : évalue le modèle sur les segments CIF et écrit metrics.json."""
    parser = argparse.ArgumentParser(prog="cifci-evaluate")
    parser.add_argument("--features", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    import joblib
    import pandas as pd

    from cifci.evaluate.metrics import bootstrap_ci, global_metrics, segment_metrics

    cfg = get_config()
    artifact = joblib.load(args.model)
    df = pd.read_csv(args.features)
    feats = list(cfg.features["list"])
    X = df[feats]
    model, calibrator = artifact["model"], artifact["calibrator"]
    prob = calibrator.predict(model.predict_proba(X)[:, 1])
    y = df["is_default"]

    global_m = global_metrics(y, prob)
    ci = bootstrap_ci(y, pd.Series(prob), n_splits=30, seed=42)
    seg_df = pd.DataFrame({"prob": prob, "is_default": y, "history_len": df["n_loans"].to_numpy()})
    seg = segment_metrics(seg_df)

    report = {
        "global": global_m,
        "bootstrap_ci": ci,
        "segments": seg.to_dict("records"),
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print(f"Évaluation écrite : {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    sub = sys.argv[1] if len(sys.argv) > 1 else ""
    rest = sys.argv[2:]
    if sub in ("prepare-features", "prepare"):
        return _prepare_features(rest)
    if sub == "train":
        return _train(rest)
    if sub == "evaluate":
        return _evaluate(rest)
    print(__doc__)
    return 1


def prepare_main() -> int:
    return _prepare_features(sys.argv[1:])


def train_main() -> int:
    return _train(sys.argv[1:])


def evaluate_main() -> int:
    return _evaluate(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
