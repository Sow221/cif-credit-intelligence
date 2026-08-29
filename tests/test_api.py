"""Tests de l'API de scoring (FastAPI / TestClient)."""

from __future__ import annotations

import warnings

import pytest
from fastapi.testclient import TestClient

from cifci.api.app import DynamicScoreRequest, _feature_names, app


@pytest.fixture(scope="module")
def client() -> TestClient:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return TestClient(app)


@pytest.fixture(scope="module")
def payload() -> dict:
    from cifci.data.ingest import load_customers, load_loans
    from cifci.features.build import prepare_feature_matrix

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cust, loans = load_customers(), load_loans()
        X, _ = prepare_feature_matrix(cust, loans)
    return {k: float(v) for k, v in X.iloc[0].items()}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["model_loaded"] is True


def test_score_returns_probability_and_decision(client, payload):
    r = client.post("/score", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert 0.0 <= body["probability_default"] <= 1.0
    assert body["decision"] in {"APPROBATION", "REVUE_HUMAINE", "AJUSTEMENT", "REFUS"}


def test_explain_returns_local_contributions(client, payload):
    r = client.post("/explain", json=payload)
    assert r.status_code == 200
    expl = r.json()["explanation"]
    assert len(expl) > 0
    assert "feature" in expl[0] and "shap_value" in expl[0]


def test_score_rejects_forbidden_extra_column(client, payload):
    contaminated = {**payload, "p_default_true": 0.5}
    r = client.post("/score", json=contaminated)
    assert r.status_code == 422


def test_dynamic_schema_has_25_features():
    feats = _feature_names()
    assert len(feats) == 25
    schema = DynamicScoreRequest.model_json_schema()
    assert set(feats) <= set(schema["properties"].keys())
