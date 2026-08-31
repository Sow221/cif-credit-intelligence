"""Service application (P0, etape 2).

Orchestre la creation, la lecture et le lifecycle de l'application.
Le lifecycle (DRAFT -> SUBMITTED -> ...) est distinct de la decision metier.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.core.exceptions import InvalidStateTransitionError, NotFoundError
from src.db.models import Application
from src.repositories.application_repository import ApplicationRepository
from src.schemas.application import ApplicationCreate, ApplicationStatus


# Transitions autorisees du lifecycle (consigne section 4 P0.3).
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "DRAFT": {"SUBMITTED", "CANCELLED"},
    "SUBMITTED": {"DATA_VALIDATION", "CANCELLED"},
    "DATA_VALIDATION": {"PROFILED", "REVIEW", "CANCELLED"},
    "PROFILED": {"SCORED", "REVIEW", "CANCELLED"},
    "SCORED": {"REVIEW", "DECIDED", "CANCELLED"},
    "REVIEW": {"SCORED", "DECIDED", "CANCELLED", "SUBMITTED"},
    "DECIDED": {"DISBURSED", "CANCELLED"},
    "DISBURSED": {"ACTIVE"},
    "ACTIVE": {"COMPLETED", "DEFAULT"},
    "COMPLETED": set(),
    "DEFAULT": set(),
    "CANCELLED": set(),
}


class ApplicationService:
    """Logique metier de l'application de credit."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ApplicationRepository(db)
        self._audit = AuditService(db)

    def create_application(
        self,
        *,
        institution_id: uuid.UUID,
        payload: ApplicationCreate,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Application:
        application = self._repo.create(
            institution_id=institution_id,
            client_id=payload.client_id,
            product_id=payload.product_id,
            requested_amount=payload.requested_amount,
            currency=payload.currency,
            requested_term=payload.requested_term,
            purpose=payload.purpose,
        )
        self._db.flush()
        self._audit.log(
            AuditEventType.APPLICATION_CREATED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="application",
            entity_id=str(application.application_id),
            request_id=request_id,
            details={
                "client_id": str(payload.client_id),
                "product_id": payload.product_id,
                "amount": payload.requested_amount,
            },
        )
        self._db.commit()
        self._db.refresh(application)
        return application

    def get_application(
        self, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> Application:
        application = self._repo.get(application_id, institution_id)
        if application is None:
            raise NotFoundError(f"Application {application_id} introuvable")
        return application

    def list_applications(self, institution_id: uuid.UUID) -> list[Application]:
        return self._repo.list(institution_id)

    def transition(
        self,
        *,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        to_status: ApplicationStatus,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Application:
        application = self.get_application(application_id, institution_id)
        target = to_status.value
        if target not in ALLOWED_TRANSITIONS.get(application.status, set()):
            raise InvalidStateTransitionError(
                f"Transition {application.status} -> {target} interdite",
                details={"from": application.status, "to": target},
            )
        self._repo.update_status(application, target)
        self._db.flush()
        self._audit.log(
            AuditEventType.APPLICATION_UPDATED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="application",
            entity_id=str(application.application_id),
            request_id=request_id,
            details={"from_status": application.status, "to_status": target},
        )
        self._db.commit()
        self._db.refresh(application)
        return application
