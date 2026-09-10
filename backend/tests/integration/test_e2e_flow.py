from __future__ import annotations

from src.features.data_quality import DataQualityService
from src.features.feature_engine import FeatureEngineService
from src.features.information_profiler import InformationProfilerService
from src.models.calibration import CalibrationService
from src.models.risk_engine import RiskEngine
from src.models.uncertainty import UncertaintyService
from src.services.decision_engine import DecisionEngine, DecisionInput
from src.services.eligibility_service import EligibilityService


def test_full_decision_flow():
    eligibility = EligibilityService()
    quality = DataQualityService()
    profiler = InformationProfilerService()
    feature_engine = FeatureEngineService()
    risk_engine = RiskEngine()
    calibration = CalibrationService()
    uncertainty = UncertaintyService()
    decision_engine = DecisionEngine()

    app_data = {"requested_amount": 500000, "requested_term": 12}
    elig = eligibility.check(app_data)
    assert elig.eligible is True

    records = [
        {
            "field_name": "income",
            "field_value": "500000",
            "data_type": "financial",
            "observed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            "source_id": __import__("uuid").uuid4(),
        }
    ]
    qr = quality.check(records)
    assert qr.overall.value in ("PASS", "WARNING")

    profile = profiler.profile(records, {"total_applications": 3, "total_loans": 2})
    assert profile.information_state in ("THIN_FILE", "FULL_FILE")

    features = feature_engine.build_features(
        {
            "monthly_income": 500000,
            "debt_to_income": 0.2,
            "repayment_rate": 0.9,
            "savings_balance": 100000,
        },
        "MINIMAL",
    )
    pd_raw = risk_engine.score(features)
    pd_cal = calibration.calibrate(pd_raw)
    unc = uncertainty.assess(pd_raw, features)

    decision_input = DecisionInput(
        eligible=elig.eligible,
        pd_calibrated=pd_cal,
        uncertainty_level=unc.level,
        information_state=profile.information_state,
        data_quality=qr.overall.value,
        policy={"approve_threshold": 0.7, "decline_threshold": 0.3},
    )
    decision = decision_engine.decide(decision_input)
    assert decision.recommendation in ("APPROVE", "REVIEW", "DECLINE")
