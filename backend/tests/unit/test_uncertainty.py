from __future__ import annotations

from src.models.uncertainty import UncertaintyService


def test_low_uncertainty():
    service = UncertaintyService()
    features = {"monthly_income": 500000, "savings_balance": 100000, "debt_to_income": 0.2}
    result = service.assess(0.5, features)
    assert result.level in ("LOW", "MEDIUM")
    assert result.method == "EVIDENCE_BASED"
    assert result.score != (1 - 0.5)


def test_high_uncertainty():
    service = UncertaintyService()
    features = {"a": 0, "b": 0, "c": 0, "d": 0, "e": 0, "income_stability": 0}
    result = service.assess(0.5, features)
    assert result.level == "HIGH"
