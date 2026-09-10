from __future__ import annotations

from typing import Any


class StandardError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {"error": {"code": self.code, "message": self.message, "details": self.details}}


class InvalidRequestError(StandardError):
    def __init__(self, message: str = "Requête invalide", details: dict[str, Any] | None = None):
        super().__init__("INVALID_REQUEST", message, details)


class ValidationError(StandardError):
    def __init__(
        self, message: str = "Erreur de validation", details: dict[str, Any] | None = None
    ):
        super().__init__("VALIDATION_ERROR", message, details)


class AuthenticationRequiredError(StandardError):
    def __init__(self, message: str = "Authentification requise"):
        super().__init__("AUTHENTICATION_REQUIRED", message)


class ForbiddenError(StandardError):
    def __init__(self, message: str = "Accès interdit"):
        super().__init__("FORBIDDEN", message)


class ResourceNotFoundError(StandardError):
    def __init__(self, resource: str = "Ressource", resource_id: str = ""):
        super().__init__(
            "RESOURCE_NOT_FOUND", f"{resource} introuvable", {"resource_id": resource_id}
        )


class ConsentRequiredError(StandardError):
    def __init__(self, source_id: str = ""):
        super().__init__(
            "CONSENT_REQUIRED", "Consentement requis pour cette source", {"source_id": source_id}
        )


class ConsentRefusedError(StandardError):
    def __init__(self, source_id: str = ""):
        super().__init__("CONSENT_REFUSED", "Consentement refusé", {"source_id": source_id})


class DataQualityFailureError(StandardError):
    def __init__(
        self, message: str = "Échec qualité données", details: dict[str, Any] | None = None
    ):
        super().__init__("DATA_QUALITY_FAILURE", message, details)


class DataTemporalityFailureError(StandardError):
    def __init__(self, message: str = "Données postérieures à la demande"):
        super().__init__("DATA_TEMPORALITY_FAILURE", message)


class SourceUnavailableError(StandardError):
    def __init__(self, source_id: str = ""):
        super().__init__(
            "SOURCE_UNAVAILABLE", "Source de données indisponible", {"source_id": source_id}
        )


class FeatureNotAvailableError(StandardError):
    def __init__(self, feature: str = ""):
        super().__init__(
            "FEATURE_NOT_AVAILABLE", f"Feature non disponible: {feature}", {"feature": feature}
        )


class ModelNotAvailableError(StandardError):
    def __init__(self) -> None:
        super().__init__("MODEL_NOT_AVAILABLE", "Modèle indisponible")


class ModelNotApprovedError(StandardError):
    def __init__(self, model_version: str = ""):
        super().__init__(
            "MODEL_NOT_APPROVED",
            "Modèle non approuvé pour production",
            {"model_version": model_version},
        )


class ModelVersionMismatchError(StandardError):
    def __init__(self) -> None:
        super().__init__("MODEL_VERSION_MISMATCH", "Version du modèle incohérente")


class CalibrationUnavailableError(StandardError):
    def __init__(self) -> None:
        super().__init__("CALIBRATION_UNAVAILABLE", "Calibration indisponible")


class UncertaintyUnavailableError(StandardError):
    def __init__(self) -> None:
        super().__init__("UNCERTAINTY_UNAVAILABLE", "Évaluation d'incertitude indisponible")


class DecisionPolicyNotFoundError(StandardError):
    def __init__(self, product_id: str = ""):
        super().__init__(
            "DECISION_POLICY_NOT_FOUND",
            "Politique de décision introuvable",
            {"product_id": product_id},
        )


class DecisionNotAllowedError(StandardError):
    def __init__(self, message: str = "Décision non autorisée"):
        super().__init__("DECISION_NOT_ALLOWED", message)


class OverrideReasonRequiredError(StandardError):
    def __init__(self) -> None:
        super().__init__("OVERRIDE_REASON_REQUIRED", "Justification obligatoire pour un override")


class InvalidStateTransitionError(StandardError):
    def __init__(self, current: str, target: str):
        super().__init__("INVALID_STATE_TRANSITION", f"Transition invalide: {current} → {target}")


class IdempotencyConflictError(StandardError):
    def __init__(self) -> None:
        super().__init__("IDEMPOTENCY_CONFLICT", "Conflit d'idempotence")


class TenantAccessDeniedError(StandardError):
    def __init__(self) -> None:
        super().__init__("TENANT_ACCESS_DENIED", "Accès interdit à cette institution")


class ExternalProviderError(StandardError):
    def __init__(self, provider: str = ""):
        super().__init__("EXTERNAL_PROVIDER_ERROR", f"Erreur provider externe: {provider}")


class RateLimitedError(StandardError):
    def __init__(self) -> None:
        super().__init__("RATE_LIMITED", "Trop de requêtes, réessayez")


class InternalError(StandardError):
    def __init__(self, message: str = "Erreur interne"):
        super().__init__("INTERNAL_ERROR", message)
