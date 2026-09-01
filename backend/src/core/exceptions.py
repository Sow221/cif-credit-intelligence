"""Contrat d'erreur standard et exceptions metier (P0).

Toutes les erreurs metier exposent un corps conforme :
    {
      "error": {
        "code": "DATA_QUALITY_FAILURE",
        "message": "Readable message",
        "details": {}
      }
    }

Le handler global (main.py) convertit les exceptions metier en reponse HTTP
conforme au contrat (consigne sections 40, 41, 67).
"""

from typing import Any, Dict, Optional


class StandardError(Exception):
    """Exception metier avec code standardise et corps standard."""

    code = "INTERNAL_ERROR"
    status_code = 400

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        *,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.request_id = request_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ErrorCode:
    """Codes d'erreur standard (consigne section 41)."""

    INVALID_REQUEST = "INVALID_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    FORBIDDEN = "FORBIDDEN"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    CONSENT_REQUIRED = "CONSENT_REQUIRED"
    CONSENT_REFUSED = "CONSENT_REFUSED"
    DATA_QUALITY_FAILURE = "DATA_QUALITY_FAILURE"
    DATA_TEMPORALITY_FAILURE = "DATA_TEMPORALITY_FAILURE"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    FEATURE_NOT_AVAILABLE = "FEATURE_NOT_AVAILABLE"
    MODEL_NOT_AVAILABLE = "MODEL_NOT_AVAILABLE"
    MODEL_NOT_APPROVED = "MODEL_NOT_APPROVED"
    MODEL_VERSION_MISMATCH = "MODEL_VERSION_MISMATCH"
    CALIBRATION_UNAVAILABLE = "CALIBRATION_UNAVAILABLE"
    UNCERTAINTY_UNAVAILABLE = "UNCERTAINTY_UNAVAILABLE"
    DECISION_POLICY_NOT_FOUND = "DECISION_POLICY_NOT_FOUND"
    DECISION_NOT_ALLOWED = "DECISION_NOT_ALLOWED"
    OVERRIDE_REASON_REQUIRED = "OVERRIDE_REASON_REQUIRED"
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    TENANT_ACCESS_DENIED = "TENANT_ACCESS_DENIED"
    EXTERNAL_PROVIDER_ERROR = "EXTERNAL_PROVIDER_ERROR"
    LINEAGE = "LINEAGE"
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class NotFoundError(StandardError):
    code = ErrorCode.RESOURCE_NOT_FOUND
    status_code = 404


class ForbiddenError(StandardError):
    code = ErrorCode.FORBIDDEN
    status_code = 403


class AuthenticationRequiredError(StandardError):
    code = ErrorCode.AUTHENTICATION_REQUIRED
    status_code = 401


class TenantAccessDeniedError(StandardError):
    code = ErrorCode.TENANT_ACCESS_DENIED
    status_code = 403


class DataQualityError(StandardError):
    code = ErrorCode.DATA_QUALITY_FAILURE
    status_code = 422


class TemporalGuardError(StandardError):
    code = ErrorCode.DATA_TEMPORALITY_FAILURE
    status_code = 422


class ConsentRequiredError(StandardError):
    code = ErrorCode.CONSENT_REQUIRED
    status_code = 403


class ConsentRefusedError(StandardError):
    code = ErrorCode.CONSENT_REFUSED
    status_code = 403


class ModelNotApprovedError(StandardError):
    code = ErrorCode.MODEL_NOT_APPROVED
    status_code = 409


class ModelNotAvailableError(StandardError):
    code = ErrorCode.MODEL_NOT_AVAILABLE
    status_code = 503


class FeatureNotAvailableError(StandardError):
    code = ErrorCode.FEATURE_NOT_AVAILABLE
    status_code = 422


class SourceUnavailableError(StandardError):
    code = ErrorCode.SOURCE_UNAVAILABLE
    status_code = 503


class DecisionPolicyNotFoundError(StandardError):
    code = ErrorCode.DECISION_POLICY_NOT_FOUND
    status_code = 409


class DecisionNotAllowedError(StandardError):
    code = ErrorCode.DECISION_NOT_ALLOWED
    status_code = 409


class OverrideReasonRequiredError(StandardError):
    code = ErrorCode.OVERRIDE_REASON_REQUIRED
    status_code = 422


class InvalidStateTransitionError(StandardError):
    code = ErrorCode.INVALID_STATE_TRANSITION
    status_code = 409


class IdempotencyConflictError(StandardError):
    code = ErrorCode.IDEMPOTENCY_CONFLICT
    status_code = 409


class LineageError(StandardError):
    code = ErrorCode.LINEAGE
    status_code = 409


# Registry pour le handler global.
ERROR_BY_CODE = {
    cls.code: cls
    for cls in [
        NotFoundError,
        ForbiddenError,
        AuthenticationRequiredError,
        TenantAccessDeniedError,
        DataQualityError,
        TemporalGuardError,
        ConsentRequiredError,
        ConsentRefusedError,
        ModelNotApprovedError,
        ModelNotAvailableError,
        FeatureNotAvailableError,
        SourceUnavailableError,
        DecisionPolicyNotFoundError,
        DecisionNotAllowedError,
        OverrideReasonRequiredError,
        InvalidStateTransitionError,
        IdempotencyConflictError,
        LineageError,
    ]
}
