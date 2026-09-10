from __future__ import annotations

from src.models.risk_engine import RiskEngine


def test_heuristic_high_risk():
    engine = RiskEngine()
    features = {"debt_to_income": 0.8, "repayment_rate": 0.3, "savings_balance": 10000}
    score = engine.score(features)
    assert score > 0.5


def test_heuristic_low_risk():
    engine = RiskEngine()
    features = {"debt_to_income": 0.1, "repayment_rate": 0.95, "savings_balance": 200000}
    score = engine.score(features)
    assert score < 0.5


def test_score_bounds():
    engine = RiskEngine()
    features = {}
    score = engine.score(features)
    assert 0.0 <= score <= 1.0
