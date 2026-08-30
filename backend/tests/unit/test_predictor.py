"""Tests du predictor (reponse.txt, etape 9 - flux complet)."""

import pytest

from src.config.settings import Settings
from src.models.predictor import Predictor


@pytest.fixture(scope="module")
def predictor() -> Predictor:
    return Predictor(Settings().model_path)


def _payload() -> dict:
    return {
        "customer_id": 12345,
        "age": 35,
        "seniority_months": 48,
        "monthly_income": 850,
        "current_savings": 1200,
        "n_past_loans": 3,
        "current_loan_request": 500,
        "current_loan_duration": 12,
        "savings_history": [{"month": i, "balance": 1000 + i * 10} for i in range(24)],
        "loan_history": [
            {
                "loan_id": 1,
                "amount": 400,
                "repayment_regularity": 0.92,
                "max_dpd": 0,
                "status": "completed",
            },
            {
                "loan_id": 2,
                "amount": 600,
                "repayment_regularity": 0.85,
                "max_dpd": 15,
                "status": "completed",
            },
            {
                "loan_id": 3,
                "amount": 350,
                "repayment_regularity": 0.78,
                "max_dpd": 45,
                "status": "completed",
            },
        ],
    }


def test_predict_returns_pd_in_range(predictor):
    pd_score = predictor.predict_pd(_payload())
    assert isinstance(pd_score, float)
    assert 0.0 <= pd_score <= 1.0


def test_feature_vector_25(predictor):
    vec = predictor.feature_vector(_payload())
    assert len(vec) == 25


def test_version_shape(predictor):
    assert predictor.model_version.startswith("MODEL_OFFICIAL")
