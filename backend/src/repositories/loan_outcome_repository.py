"""Repository des loan outcomes (P0, etape 18 / 36).

Scope tenant par jointure avec applications.
"""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Application, LoanOutcome


class LoanOutcomeRepository:
    """Acces persistant aux outcomes."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        application_id: uuid.UUID,
        loan_id: Optional[str],
        status: Optional[str],
        outcome_date,
        days_past_due: Optional[int],
        default_status: Optional[bool],
        recovery_amount: Optional[float],
        source: Optional[str],
    ) -> LoanOutcome:
        outcome = LoanOutcome(
            application_id=application_id,
            loan_id=loan_id,
            status=status,
            outcome_date=outcome_date,
            days_past_due=days_past_due,
            default_status=default_status,
            recovery_amount=recovery_amount,
            source=source,
        )
        self._db.add(outcome)
        return outcome

    def list_for_application(
        self, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> List[LoanOutcome]:
        stmt = (
            select(LoanOutcome)
            .join(Application, Application.application_id == LoanOutcome.application_id)
            .where(LoanOutcome.application_id == application_id, Application.institution_id == institution_id)
            .order_by(LoanOutcome.created_at.desc())
        )
        return list(self._db.scalars(stmt).all())