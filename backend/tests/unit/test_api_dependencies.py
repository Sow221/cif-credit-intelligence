from __future__ import annotations

import asyncio
import uuid
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from src.core import security
from src.core.exceptions import (
    AuthenticationRequiredError,
    CalibrationUnavailableError,
    ConsentRefusedError,
    ConsentRequiredError,
    DataQualityFailureError,
    DataTemporalityFailureError,
    DecisionNotAllowedError,
    DecisionPolicyNotFoundError,
    ExternalProviderError,
    FeatureNotAvailableError,
    ForbiddenError,
    IdempotencyConflictError,
    InternalError,
    InvalidRequestError,
    InvalidStateTransitionError,
    ModelNotApprovedError,
    ModelNotAvailableError,
    ModelVersionMismatchError,
    OverrideReasonRequiredError,
    RateLimitedError,
    ResourceNotFoundError,
    SourceUnavailableError,
    TenantAccessDeniedError,
    UncertaintyUnavailableError,
    ValidationError,
)


def test_standard_error_structure():
    err = InvalidRequestError("bog")
    d = err.to_dict()
    assert d["error"]["code"] == "INVALID_REQUEST"
    assert d["error"]["message"] == "bog"
    assert d["error"]["details"] == {}


def test_all_standard_errors_instantiate():
    for cls in [
        ValidationError,
        AuthenticationRequiredError,
        ForbiddenError,
        ResourceNotFoundError,
        ConsentRequiredError,
        ConsentRefusedError,
        DataQualityFailureError,
        DataTemporalityFailureError,
        SourceUnavailableError,
        FeatureNotAvailableError,
        DecisionPolicyNotFoundError,
        DecisionNotAllowedError,
        ExternalProviderError,
        InternalError,
    ]:
        inst = cls("product_1")
        assert inst.code and inst.message
    for cls in [
        ModelNotAvailableError,
        ModelNotApprovedError,
        ModelVersionMismatchError,
        CalibrationUnavailableError,
        UncertaintyUnavailableError,
        OverrideReasonRequiredError,
        IdempotencyConflictError,
        TenantAccessDeniedError,
        RateLimitedError,
    ]:
        inst = cls()
        assert inst.code and inst.message
    transition = InvalidStateTransitionError("PENDING", "COMPLETED")
    assert transition.code == "INVALID_STATE_TRANSITION"


def test_security_hash_and_verify():
    h = security.hash_password("secret")
    assert h != "secret"
    assert security.verify_password("secret", h)
    assert not security.verify_password("wrong", h)


def test_security_tokens():
    token = security.create_access_token(
        {"sub": str(uuid.uuid4())}, expires_delta=timedelta(minutes=5)
    )
    payload = security.decode_access_token(token)
    assert payload is not None
    assert "sub" in payload
    assert security.decode_access_token("not.a.token") is None
    assert security.decode_access_token("") is None


def test_health_endpoint():
    from src.main import app

    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_openapi_docs():
    from src.main import app

    client = TestClient(app)
    resp = client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["info"]["title"] == "CIF Credit Intelligence"


def test_get_current_user_requires_bearer(db, user):
    from src.api.dependencies.auth import get_current_user
    from src.core.exceptions import AuthenticationRequiredError

    with pytest.raises(AuthenticationRequiredError):
        asyncio.run(get_current_user(authorization="Basic abc", db=db))


def test_get_current_user_invalid_token(db, user):
    from src.api.dependencies.auth import get_current_user
    from src.core.exceptions import AuthenticationRequiredError

    with pytest.raises(AuthenticationRequiredError):
        asyncio.run(get_current_user(authorization="Bearer bad.token.value", db=db))


def test_get_current_user_valid(db, user):
    from src.api.dependencies.auth import get_current_user

    token = security.create_access_token({"sub": str(user.user_id)})
    result = asyncio.run(get_current_user(authorization=f"Bearer {token}", db=db))
    assert result.user_id == user.user_id


def test_require_permission_allows(db, user):
    from src.api.dependencies.auth import get_current_user
    from src.api.dependencies.permissions import require_permission

    token = security.create_access_token({"sub": str(user.user_id)})
    current = asyncio.run(get_current_user(authorization=f"Bearer {token}", db=db))
    result = asyncio.run(require_permission("clients:read")(user=current))
    assert result.role == "CREDIT_OFFICER"


def test_require_permission_forbids(db, user):
    from src.api.dependencies.permissions import require_permission
    from src.core.exceptions import ForbiddenError

    with pytest.raises(ForbiddenError):
        asyncio.run(require_permission("models:write")(user=user))


def test_require_permission_admin_wildcard(db, institution):
    from src.api.dependencies.permissions import require_permission

    class AdminUser:
        role = "ADMIN"

    result = asyncio.run(require_permission("anything:any")(user=AdminUser()))
    assert result.role == "ADMIN"


def test_get_current_institution(db, user):
    from src.api.dependencies.tenant import get_current_institution

    inst_id = asyncio.run(get_current_institution(user=user))
    assert inst_id == user.institution_id
