from __future__ import annotations

from src.features.feature_engine import APPROVED_FEATURES, FeatureEngineService


def test_minimal_features():
    service = FeatureEngineService()
    features = service.resolve_feature_set("MINIMAL")
    assert len(features) == 5
    assert "monthly_income" in features


def test_full_features():
    service = FeatureEngineService()
    features = service.resolve_feature_set("FULL_ADMISSIBLE")
    assert len(features) == len(APPROVED_FEATURES)


def test_invalid_set():
    service = FeatureEngineService()
    try:
        service.resolve_feature_set("INVALID")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_build_features():
    service = FeatureEngineService()
    raw = {"monthly_income": 500000, "savings_balance": 100000}
    features = service.build_features(raw, "MINIMAL")
    assert features["monthly_income"] == 500000
    assert features["savings_balance"] == 100000


def test_snapshot_hash():
    service = FeatureEngineService()
    h1 = service.compute_snapshot_hash({"a": 1, "b": 2})
    h2 = service.compute_snapshot_hash({"b": 2, "a": 1})
    assert h1 == h2
    assert len(h1) == 64
