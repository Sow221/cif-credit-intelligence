from __future__ import annotations

from src.core.exceptions import (
    ForbiddenError,
    ModelNotApprovedError,
    OverrideReasonRequiredError,
    ResourceNotFoundError,
    StandardError,
)


def test_standard_error_format():
    err = StandardError("TEST_CODE", "Test message", {"key": "value"})
    d = err.to_dict()
    assert d["error"]["code"] == "TEST_CODE"
    assert d["error"]["message"] == "Test message"
    assert d["error"]["details"]["key"] == "value"


def test_forbidden_error():
    err = ForbiddenError("AccÃ¨s interdit")
    assert err.code == "FORBIDDEN"


def test_resource_not_found():
    err = ResourceNotFoundError("Client", "123")
    assert err.code == "RESOURCE_NOT_FOUND"


def test_override_reason_required():
    err = OverrideReasonRequiredError()
    assert err.code == "OVERRIDE_REASON_REQUIRED"


def test_model_not_approved():
    err = ModelNotApprovedError("v1.0")
    assert err.code == "MODEL_NOT_APPROVED"
