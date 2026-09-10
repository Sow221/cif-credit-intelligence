from __future__ import annotations

from src.services.decision_engine import DecisionEngine, DecisionInput


def test_decline_ineligible():
    engine = DecisionEngine()
    inputs = DecisionInput(
        eligible=False,
        pd_calibrated=0.5,
        uncertainty_level="LOW",
        information_state="FULL_FILE",
        data_quality="PASS",
        policy={"approve_threshold": 0.7, "decline_threshold": 0.3},
    )
    result = engine.decide(inputs)
    assert result.recommendation == "DECLINE"


def test_approve_low_risk():
    engine = DecisionEngine()
    inputs = DecisionInput(
        eligible=True,
        pd_calibrated=0.8,
        uncertainty_level="LOW",
        information_state="FULL_FILE",
        data_quality="PASS",
        policy={"approve_threshold": 0.7, "decline_threshold": 0.3},
    )
    result = engine.decide(inputs)
    assert result.recommendation == "APPROVE"


def test_review_high_uncertainty():
    engine = DecisionEngine()
    inputs = DecisionInput(
        eligible=True,
        pd_calibrated=0.5,
        uncertainty_level="HIGH",
        information_state="FULL_FILE",
        data_quality="PASS",
        policy={"approve_threshold": 0.7, "decline_threshold": 0.3},
    )
    result = engine.decide(inputs)
    assert result.recommendation == "REVIEW"


def test_review_thin_file():
    engine = DecisionEngine()
    inputs = DecisionInput(
        eligible=True,
        pd_calibrated=0.5,
        uncertainty_level="LOW",
        information_state="THIN_FILE",
        data_quality="PASS",
        policy={"approve_threshold": 0.7, "decline_threshold": 0.3},
    )
    result = engine.decide(inputs)
    assert result.recommendation == "REVIEW"
