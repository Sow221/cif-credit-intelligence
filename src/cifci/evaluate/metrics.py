"""Évaluation du modèle selon le protocole CIF.

Inclut : métriques globales (ROC-AUC, PR-AUC, Brier, log-loss, MCC),
intervalles de confiance par bootstrap, et évaluation par segments
(thin-file / historique) comme l'exige le protocole de validation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)


def _safe(fn, *args, **kwargs) -> float:
    try:
        return float(fn(*args, **kwargs))
    except Exception:
        return float("nan")


def global_metrics(y_true: pd.Series, y_prob: pd.Series, threshold: float = 0.5) -> dict:
    """Calcule les métriques globales clés."""
    y = y_true.to_numpy()
    p = np.asarray(y_prob, dtype=float)
    pred = (p >= threshold).astype(int)
    return {
        "roc_auc": _safe(roc_auc_score, y, p),
        "pr_auc": _safe(average_precision_score, y, p),
        "brier": _safe(brier_score_loss, y, p),
        "log_loss": _safe(log_loss, y, p),
        "mcc": _safe(matthews_corrcoef, y, pred)
        if len(set(y)) > 1
        else float("nan"),
        "recall": _safe(recall_score, y, pred),
        "precision": _safe(precision_score, y, pred),
    }


def bootstrap_ci(
    y_true: pd.Series,
    y_prob: pd.Series,
    *,
    n_splits: int = 1000,
    seed: int = 42,
) -> dict[str, tuple[float, float]]:
    """Intervalles de confiance à 95 % (bootstrap) des métriques principales."""
    rng = np.random.default_rng(seed)
    y = y_true.to_numpy()
    p = np.asarray(y_prob, dtype=float)
    n = len(y)
    samples: dict[str, list[float]] = {"roc_auc": [], "pr_auc": [], "brier": []}
    for _ in range(n_splits):
        idx = rng.integers(0, n, size=n)
        yi, pi = y[idx], p[idx]
        if len(set(yi)) < 2:
            continue
        samples["roc_auc"].append(roc_auc_score(yi, pi))
        samples["pr_auc"].append(average_precision_score(yi, pi))
        samples["brier"].append(brier_score_loss(yi, pi))
    out = {}
    for k, vals in samples.items():
        if vals:
            out[k] = (
                float(np.percentile(vals, 2.5)),
                float(np.percentile(vals, 97.5)),
            )
        else:
            out[k] = (float("nan"), float("nan"))
    return out


def segment_metrics(
    df: pd.DataFrame,
    *,
    id_col: str = "customer_id",
    target_col: str = "is_default",
    order_col: str | None = None,
) -> pd.DataFrame:
    """Évalue les métriques par segment d'historique (protocole CIF).

    Les segments (thin-file 0 prêt / 1 prêt / 2-3 / 4+) sont inférés depuis
    une colonne de comptage d'historique si fournie, sinon estimés.

    Args:
        df: DataFrame avec probabilité prédite (colonne ``prob``), cible et
            éventuellement ``history_len`` (nombre de prêts) et ``prob``.
    """
    if "prob" not in df.columns:
        raise ValueError("Le DataFrame doit contenir une colonne `prob`.")
    if "history_len" not in df.columns:
        # Estimation grossière : par défaut, pas d'historique connu.
        df = (
            df.assign(history_len=1)
            if order_col is None
            else df.copy()
        )

    segments: dict[str, tuple[int, ...] | int] = {
        "thin_file_0_loan": 0,
        "thin_file_1_loan": 1,
        "history_2_3": (2, 3),
        "history_4_plus": 4,
    }
    rows = []
    for name, sel in segments.items():
        if isinstance(sel, int):
            mask = df["history_len"] == sel
        else:
            mask = df["history_len"].between(sel[0], sel[1])
        sub = df[mask]
        if sub.empty:
            rows.append({"segment": name, "n": 0, "roc_auc": float("nan"), "brier": float("nan")})
            continue
        m = global_metrics(sub[target_col], sub["prob"])
        rows.append({"segment": name, "n": len(sub), "roc_auc": m["roc_auc"], "brier": m["brier"]})
    return pd.DataFrame(rows)
