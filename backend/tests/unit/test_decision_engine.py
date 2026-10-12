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
        policy={"approve_max_pd": 0.05, "decline_min_pd": 0.30},
    )
    result = engine.decide(inputs)
    assert result.recommendation == "DECLINE"


def test_approve_low_risk():
    engine = DecisionEngine()
    inputs = DecisionInput(
        eligible=True,
        pd_calibrated=0.02,
        uncertainty_level="LOW",
        information_state="FULL_FILE",
        data_quality="PASS",
        policy={"approve_max_pd": 0.05, "decline_min_pd": 0.30},
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
        policy={"approve_max_pd": 0.05, "decline_min_pd": 0.30},
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
        policy={"approve_max_pd": 0.05, "decline_min_pd": 0.30},
    )
    result = engine.decide(inputs)
    assert result.recommendation == "REVIEW"


def _full_file(pd_value: float) -> DecisionInput:
    return DecisionInput(
        eligible=True,
        pd_calibrated=pd_value,
        uncertainty_level="LOW",
        information_state="FULL_FILE",
        data_quality="PASS",
        policy={"approve_max_pd": 0.05, "decline_min_pd": 0.30},
    )


def test_high_default_probability_is_never_approved():
    """Régression : une probabilité de défaut élevée ne doit jamais être approuvée."""
    assert DecisionEngine().decide(_full_file(0.80)).recommendation == "DECLINE"


def test_grey_zone_goes_to_review():
    assert DecisionEngine().decide(_full_file(0.15)).recommendation == "REVIEW"


def test_decision_is_monotonic_in_risk():
    order = {"APPROVE": 0, "REVIEW": 1, "DECLINE": 2}
    grid = [i / 100 for i in range(0, 101)]
    ranks = [order[DecisionEngine().decide(_full_file(p)).recommendation] for p in grid]
    assert ranks == sorted(ranks)


def test_invalid_policy_is_rejected():
    import pytest

    bad = _full_file(0.1)
    bad.policy = {"approve_max_pd": 0.5, "decline_min_pd": 0.3}
    with pytest.raises(ValueError):
        DecisionEngine().decide(bad)
