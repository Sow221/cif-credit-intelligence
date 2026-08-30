"""Tests du feature service (reponse.txt : transformation payload -> 25 features,
et comportement Thin-File : ne pas remplir de zeros)."""

import pytest

from src.features.registry import FeatureRegistry
from src.services.feature_service import FeatureService, FeatureServiceError


def _make_payload() -> dict:
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


def test_compute_25_features():
    features = FeatureService.compute_all_features(_make_payload())
    assert len(features) == 25, f"Attendu 25 features, obtenu {len(features)}"


def test_feature_order_matches_registry():
    features = FeatureService.compute_all_features(_make_payload())
    assert list(features.keys()) == FeatureRegistry.all_features()


def test_direct_features_values():
    features = FeatureService.compute_all_features(_make_payload())
    assert features["age"] == 35
    assert features["loan_to_savings_ratio"] == 500 / 1201
    assert features["seniority_years"] == 4.0
    assert features["n_loans"] == 3


def test_thin_file_detecte_avec_has_history_false():
    payload = _make_payload()
    payload["has_history"] = False
    assert FeatureService.is_thin_file(payload) is True


def test_thin_file_detecte_sans_histoires():
    payload = {
        "age": 35,
        "monthly_income": 850,
        "current_savings": 1200,
        "n_past_loans": 0,
        "current_loan_request": 500,
        "current_loan_duration": 12,
    }
    assert FeatureService.is_thin_file(payload) is True


def test_thin_file_ne_pas_remplir_de_zeros():
    payload = {
        "age": 35,
        "seniority_months": 0,
        "monthly_income": 850,
        "current_savings": 1200,
        "n_past_loans": 0,
        "current_loan_request": 500,
        "current_loan_duration": 12,
    }
    with pytest.raises(FeatureServiceError) as excinfo:
        FeatureService.compute_all_features(payload)
    assert "Thin-File" in str(excinfo.value)


def test_payload_sans_historique_rejete():
    payload = _make_payload()
    payload.pop("savings_history")
    payload.pop("loan_history")
    with pytest.raises(FeatureServiceError) as excinfo:
        FeatureService.compute_all_features(payload)
    assert "Thin-File" in str(excinfo.value)


def test_champs_de_base_manquants_rejetes():
    payload = _make_payload()
    payload.pop("monthly_income")
    with pytest.raises(FeatureServiceError) as excinfo:
        FeatureService.compute_all_features(payload)
    assert "Champs de base manquants" in str(excinfo.value)
