"""Tests d'integration de l'API (FastAPI TestClient).

Couvre les cas specifes :
- prediction avec historique complet        -> 200, pd_score present
- has_history=false                         -> 200, REVUE_HUMAINE, thin_file
- sans historique (ni flag ni listes)        -> 200, REVUE_HUMAINE
- age negatif                               -> 422
- post sans JWT                             -> 401
- get /health                               -> 200
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.api.middleware.auth import create_access_token  # noqa: E402
from src.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def auth_headers() -> dict:
    token = create_access_token(subject="test-user")
    return {"Authorization": f"Bearer {token}"}


def full_payload() -> dict:
    return {
        "customer_id": 1,
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


def minimal_payload() -> dict:
    return {
        "customer_id": 2,
        "age": 28,
        "seniority_months": 6,
        "monthly_income": 1800.0,
        "current_savings": 500.0,
        "n_past_loans": 0,
        "current_loan_request": 2000.0,
        "current_loan_duration": 12,
    }


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ("ok", "degraded")


def test_predict_with_full_history_returns_pd(client):
    response = client.post("/v1/predict", json=full_payload(), headers=auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["pd_score"] is not None
    assert body["is_thin_file"] is False
    assert body["request_id"]


def test_predict_thin_file_flag_returns_revue_humaine(client):
    payload = full_payload()
    payload["has_history"] = False
    response = client.post("/v1/predict", json=payload, headers=auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["is_thin_file"] is True
    assert body["pd_score"] is None
    assert body["recommendation"]["decision"] == "REVUE_HUMAINE"


def test_predict_without_history_returns_revue_humaine(client):
    response = client.post(
        "/v1/predict",
        json=minimal_payload(),
        headers=auth_headers(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_thin_file"] is True
    assert body["recommendation"]["decision"] == "REVUE_HUMAINE"


def test_predict_negative_age_returns_422(client):
    payload = full_payload()
    payload["age"] = -5
    response = client.post("/v1/predict", json=payload, headers=auth_headers())
    assert response.status_code == 422


def test_predict_without_jwt_returns_401(client):
    response = client.post("/v1/predict", json=full_payload())
    assert response.status_code == 401
