from __future__ import annotations

from src.audit.audit_service import AuditService


def test_event_types_complete():
    expected = {
        "APPLICATION_CREATED",
        "APPLICATION_UPDATED",
        "DATA_RECEIVED",
        "DATA_VALIDATED",
        "CONSENT_CREATED",
        "CONSENT_CHANGED",
        "PROFILE_CREATED",
        "FEATURE_SNAPSHOT_CREATED",
        "SCORE_CREATED",
        "UNCERTAINTY_CREATED",
        "DECISION_RECOMMENDED",
        "REVIEW_STARTED",
        "REVIEW_COMPLETED",
        "DECISION_MADE",
        "OVERRIDE_CREATED",
        "OUTCOME_RECEIVED",
        "MODEL_CREATED",
        "MODEL_VALIDATED",
        "MODEL_PROMOTED",
        "MODEL_RETIRED",
        "POLICY_CREATED",
        "POLICY_CHANGED",
        "CONFIG_CHANGED",
        "LOGIN",
        "LOGOUT",
        "ACCESS_DENIED",
    }
    assert expected.issubset(AuditService.EVENT_TYPES)
    assert len(AuditService.EVENT_TYPES) >= 26
