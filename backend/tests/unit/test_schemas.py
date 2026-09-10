from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.schemas.application_data import (
    ApplicationDataBase,
    SubmitDataRequest,
)
from src.schemas.audit import AuditEventResponse
from src.schemas.information_profile import InformationProfileResponse
from src.schemas.scoring import ScoreResponse
from src.schemas.uncertainty import UncertaintyResponse


def test_application_data_base():
    r = ApplicationDataBase(
        source_id=uuid.uuid4(),
        field_name="income",
        field_value="500000",
        data_type="financial",
        observed_at=datetime.now(UTC),
    )
    assert r.field_name == "income"


def test_submit_data_request():
    rec = ApplicationDataBase(
        source_id=uuid.uuid4(),
        field_name="x",
        field_value="1",
        data_type="t",
        observed_at=datetime.now(UTC),
    )
    req = SubmitDataRequest(records=[rec])
    assert len(req.records) == 1


def test_information_profile_response():
    r = InformationProfileResponse(
        profile_id="1",
        application_id="2",
        applicant_status="ESTABLISHED",
        credit_depth="HIGH",
        financial_depth="MEDIUM",
        business_depth="LOW",
        relationship_depth="NONE",
        data_quality="GOOD",
        information_state="FULL_FILE",
        profile_version=1,
        config_version=1,
    )
    assert r.information_state == "FULL_FILE"


def test_score_response():
    r = ScoreResponse(
        prediction_id="1",
        pd_raw=0.5,
        pd_calibrated=0.45,
        model_version="v1",
        feature_set_id="fs1",
        snapshot_id="snap1",
    )
    assert r.pd_raw == 0.5


def test_uncertainty_response():
    r = UncertaintyResponse(
        uncertainty_id="1",
        prediction_id="2",
        method="EVIDENCE_BASED",
        version="1.0",
        score=0.3,
        level="MEDIUM",
    )
    assert r.level == "MEDIUM"


def test_audit_event_response():
    r = AuditEventResponse(
        event_id="1", institution_id="inst1", event_type="LOGIN", created_at="2024-01-01"
    )
    assert r.event_type == "LOGIN"
