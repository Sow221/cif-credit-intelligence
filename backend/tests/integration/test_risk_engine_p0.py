"""Tests du risk engine (P0, etape 11).

Verifie que le RiskEngine encapsule le modele (jamais XGBClassifier/Mlflow en
appel direct), retourne pd_raw + model_version + feature_set_id + timestamp,
et reveille une erreur quand le modele est indisponible. Tests pur (aucun DB).
"""

import numpy as np
import pytest

from src.features.registry import FeatureRegistry
from src.models.risk_engine import RiskEngine, RiskScore


class StubModel:
    feature_names_in_ = FeatureRegistry.all_features()

    def predict_proba(self, X):
        return np.array([[1.0 - 0.3, 0.3]])


class StubPredictor:
    source = "file:stub"

    def __init__(self, loaded: bool = True) -> None:
        self._loaded = loaded
        self.model = StubModel() if loaded else None

    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def model_version(self) -> str:
        return "MODEL_OFFICIAL-25f"


def _payload() -> dict:
    return {
        "age": 34,
        "seniority_months": 60,
        "monthly_income": 250000,
        "current_savings": 50000,
        "n_past_loans": 2,
        "current_loan_request": 200000,
        "current_loan_duration": 12,
        "has_history": True,
        "savings_history": [{"balance": 50000}, {"balance": 52000}],
        "loan_history": [
            {"amount": 100000, "repayment_regularity": 0.9, "max_dpd": 0, "status": "paid"},
            {"amount": 150000, "repayment_regularity": 0.8, "max_dpd": 5, "status": "paid"},
        ],
    }


def test_score_returns_full_risk_score() -> None:
    engine = RiskEngine(StubPredictor())
    features = {name: 1.0 for name in FeatureRegistry.all_features()}
    result = engine.score(features, feature_set="FULL_ADMISSIBLE")
    assert isinstance(result, RiskScore)
    assert result.pd_raw == pytest.approx(0.3)
    assert result.feature_set_id == "FULL_ADMISSIBLE"
    assert result.model_version == "MODEL_OFFICIAL-25f"
    assert result.prediction_timestamp


def test_score_payload_builds_features() -> None:
    engine = RiskEngine(StubPredictor())
    result = engine.score_payload(_payload(), feature_set="FULL_ADMISSIBLE")
    assert isinstance(result.pd_raw, float)
    assert 0.0 <= result.pd_raw <= 1.0
    assert result.feature_set_id == "FULL_ADMISSIBLE"


def test_score_raises_when_model_unavailable() -> None:
    engine = RiskEngine(StubPredictor(loaded=False))
    with pytest.raises(RuntimeError):
        engine.score({name: 1.0 for name in FeatureRegistry.all_features()})