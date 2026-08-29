"""Tests de l'entraînement, de l'évaluation et du moteur de décision."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest

from cifci.decision.engine import (
    DECISIONS,
    decide,
    decision_distribution,
    decision_for_probability,
)
from cifci.evaluate.metrics import bootstrap_ci, global_metrics, segment_metrics
from cifci.models.train import temporal_split, train_pipeline


@pytest.fixture(scope="module")
def data():
    from cifci.data.ingest import load_customers, load_loans

    return load_customers(), load_loans()


def test_temporal_split_preserves_order(data):
    cust, _ = data
    a, b = temporal_split(cust, order_col="customer_id")
    assert set(a["customer_id"]).isdisjoint(set(b["customer_id"]))
    # L'élément de tête du split train doit être antérieur (plus petit id).
    assert a["customer_id"].min() < b["customer_id"].min()


def test_train_pipeline_artifact_shape(data):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cust, loans = data
        art = train_pipeline(cust, loans)
    assert set(art.keys()) == {"model", "calibrator", "model_features", "calibration_method", "metrics_before", "metrics_after"}
    assert len(art["model_features"]) == 25
    assert art["calibration_method"] == "isotonic"
    assert "roc_auc" in art["metrics_before"] and "brier" in art["metrics_after"]


def test_train_pipeline_produces_sane_metrics(data):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cust, loans = data
        art = train_pipeline(cust, loans)
    # Un modèle performant en phase synthétique : AUC > 0.7.
    assert art["metrics_after"]["roc_auc"] > 0.7
    # La calibration doit améliorer (ou maintenir) le Brier.
    assert art["metrics_after"]["brier"] <= art["metrics_before"]["brier"] + 1e-9


def test_global_metrics_sane():
    y = pd.Series([0, 1, 1, 0, 1, 0, 1, 1, 0, 1])
    p = pd.Series([0.1, 0.9, 0.8, 0.2, 0.7, 0.3, 0.85, 0.75, 0.15, 0.95])
    m = global_metrics(y, p)
    assert 0.5 < m["roc_auc"] <= 1.0
    assert 0.0 <= m["brier"] <= 1.0
    assert m["mcc"] == m["mcc"]  # non-NaN, classes présentes


def test_bootstrap_ci_bounds():
    rng = np.random.default_rng(0)
    y = pd.Series(rng.integers(0, 2, size=500))
    p = pd.Series(rng.random(500))
    ci = bootstrap_ci(y, p, n_splits=300, seed=1)
    for _k, (lo, hi) in ci.items():
        assert lo <= hi
        assert 0.0 <= lo <= 1.0 and 0.0 <= hi <= 1.0


def test_segment_metrics_produces_segments(data):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cust, loans = data
        art = train_pipeline(cust, loans)
    X, y = __import__("cifci.features.build", fromlist=["prepare_feature_matrix"]).prepare_feature_matrix(cust, loans)
    prob = art["calibrator"].predict(art["model"].predict_proba(X)[:, 1])
    df = pd.DataFrame({"prob": prob, "is_default": y, "history_len": X["n_loans"]})
    res = segment_metrics(df)
    assert "thin_file_0_loan" in set(res["segment"])
    assert "history_4_plus" in set(res["segment"])


# --- Decision engine ---

def test_decision_thresholds_ordering():
    assert decision_for_probability(0.01) == "APPROBATION"
    assert decision_for_probability(0.10) == "REVUE_HUMAINE"
    assert decision_for_probability(0.25) == "AJUSTEMENT"
    assert decision_for_probability(0.80) == "REFUS"


def test_decision_thin_file_boost():
    out = decide([0.02, 0.02, 0.10, 0.80], history_len=[0, 2, 1, 4])
    dec = out["decision"].tolist()
    # Thin-file (0 prêt) : boosté vers REVUE_HUMAINE.
    assert dec[0] == "REVUE_HUMAINE"
    # Non thin-file à faible risque : APPROBATION.
    assert dec[1] == "APPROBATION"


def test_decision_distribution():
    out = decide([0.01, 0.05, 0.15, 0.70])
    dist = decision_distribution(out)
    assert set(dist) <= set(DECISIONS)
    assert dist["APPROBATION"] == 1
