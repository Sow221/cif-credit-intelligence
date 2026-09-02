"""Outcome service (P0, etape 18 / 36).

Ferme la boucle application -> decision -> loan -> repayment -> outcome.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.core.exceptions import NotFoundError
from src.db.models import LoanOutcome
from src.repositories.application_repository import ApplicationRepository
from src.repositories.loan_outcome_repository import LoanOutcomeRepository


class OutcomeService:
    """Orchestration des outcomes."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._outcomes = LoanOutcomeRepository(db)
        self._apps = ApplicationRepository(db)
        self._audit = AuditService(db)

    def create_outcome(
        self,
        *,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        loan_id: Optional[str],
        status: Optional[str],
        outcome_date,
        days_past_due: Optional[int],
        default_status: Optional[bool],
        recovery_amount: Optional[float],
        source: Optional[str],
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> LoanOutcome:
        app = self._apps.get(application_id, institution_id)
        if app is None:
            raise NotFoundError(f"Application {application_id} introuvable")
        outcome = self._outcomes.create(
            application_id=application_id,
            loan_id=loan_id,
            status=status,
            outcome_date=outcome_date,
            days_past_due=days_past_due,
            default_status=default_status,
            recovery_amount=recovery_amount,
            source=source,
        )
        self._db.flush()
        self._audit.log(
            AuditEventType.OUTCOME_RECEIVED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="application",
            entity_id=str(application_id),
            request_id=request_id,
            details={"loan_id": loan_id, "default_status": default_status},
        )
        self._db.commit()
        return outcome