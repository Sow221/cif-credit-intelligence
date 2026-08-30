"""Tests d'integration de l'API complete (FastAPI TestClient + PostgreSQL).

Couvre le contrat d'API complet du document :
- Sante : /health, /health/live, /health/ready
- Prediction : complet, thin-file, invalide
- Decisions : liste, detail, override
- Audit : journal
- Modeles : versions
- Securite : 401 sans JWT
- Rate limiting : 429

Chaque test est isole : les tables sont tronquees avant chaque cas.
"""

import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.api.middleware.auth import create_access_token  # noqa: E402
from src.db.session import SessionLocal  # noqa: E402
from src.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _clean_tables(client):  # noqa: ARG001
    """Nettoie les tables metier avant chaque test pour l'isolation."""
    db = SessionLocal()
    try:
        db.execute(
            text("TRUNCATE audit_log, predictions, model_versions, customers RESTART IDENTITY CASCADE")
        )
        db.commit()
    finally:
        db.close()
    yield


def auth_headers() -> dict:
    token = create_access_token(subject="test-user")
    return {"Authorization": f"Bearer {token}"}


def full_payload(customer_id: int = 100) -> dict:
    return {
        "customer_id": customer_id,
        "age": 35,
        "seniority_months": 30,
        "monthly_income": 2500.0,
        "current_savings": 8000.0,
        "n_past_loans": 2,
        "current_loan_request": 5000.0,
        "current_loan_duration": 24,
        "has_history": True,
        "savings_history": [
            {"month": 1, "balance": 6000.0},
            {"month": 2, "balance": 6500.0},
            {"month": 3, "balance": 7000.0},
            {"month": 4, "balance": 8000.0},
        ],
        "loan_history": [
            {
                "loan_id": 1,
                "amount": 3000.0,
                "repayment_regularity": 0.95,
                "max_dpd": 5,
                "status": "completed",
            },
            {
                "loan_id": 2,
                "amount": 4000.0,
                "repayment_regularity": 0.85,
                "max_dpd": 20,
                "status": "completed",
            },
        ],
    }


# ---------------------------------------------------------------- Sante ---


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_live_returns_200(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_health_ready_returns_200(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert "model_loaded" in body and "db_connected" in body


# ----------------------------------------------------------- Prediction ---


def test_predict_complet_returns_pd(client):
    response = client.post("/v1/predict", json=full_payload(), headers=auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["pd_score"] is not None
    assert body["is_thin_file"] is False


def test_predict_thin_file_returns_revue_humaine(client):
    payload = full_payload()
    payload["has_history"] = False
    response = client.post("/v1/predict", json=payload, headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["recommendation"]["decision"] == "REVUE_HUMAINE"
    assert response.json()["is_thin_file"] is True


def test_predict_invalide_returns_422(client):
    payload = full_payload()
    payload["age"] = -5
    response = client.post("/v1/predict", json=payload, headers=auth_headers())
    assert response.status_code == 422


# ------------------------------------------------------------ Decisions ---


def test_list_decisions_returns_items(client):
    client.post("/v1/predict", json=full_payload(), headers=auth_headers())
    response = client.get("/v1/decisions", headers=auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert len(body["items"]) >= 1
    assert "prediction_id" in body["items"][0]


def test_get_decision_by_id_returns_200(client):
    decision_id = _first_decision_id(client)
    response = client.get(f"/v1/decisions/{decision_id}", headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["prediction_id"] == decision_id


def test_override_decision_returns_audit_id(client):
    decision_id = _first_decision_id(client)
    response = client.post(
        f"/v1/decisions/{decision_id}/override",
        json={
            "agent_id": "agent-42",
            "decision": "REFUS",
            "justification": "Verification manuelle approfondie",
        },
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["audit_id"]


# ---------------------------------------------------------------- Audit ---


def test_get_audit_log_returns_items(client):
    decision_id = _first_decision_id(client)
    client.post(
        f"/v1/decisions/{decision_id}/override",
        json={
            "agent_id": "agent-1",
            "decision": "AJUSTEMENT",
            "justification": "Decision ajustee",
        },
        headers=auth_headers(),
    )
    response = client.get("/v1/audit", headers=auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert "audit_id" in body["items"][0]


# -------------------------------------------------------------- Modeles ---


def test_get_models_returns_200(client):
    response = client.get("/v1/models", headers=auth_headers())
    assert response.status_code == 200
    assert "items" in response.json()


# -------------------------------------------------------------- Securite ---


def test_predict_without_jwt_returns_401(client):
    response = client.post("/v1/predict", json=full_payload())
    assert response.status_code == 401


# -------------------------------------------------------- Rate limiting ---


def test_rate_limit_exceeded_returns_429(client):
    # L'endpoint le plus restrictif (drift, 5/min) permet un test rapide.
    statuses = [
        client.get("/v1/reports/drift", headers=auth_headers()).status_code
        for _ in range(7)
    ]
    assert 429 in statuses


# --------------------------------------------------------------- Helpers ---


def _first_decision_id(client) -> str:
    """Cree une prediction puis retourne son prediction_id."""
    client.post("/v1/predict", json=full_payload(), headers=auth_headers())
    decision = client.get("/v1/decisions", headers=auth_headers()).json()["items"][0]
    return decision["prediction_id"]