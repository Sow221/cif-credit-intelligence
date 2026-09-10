from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from src.models.database import LoanOutcome


class OutcomeService:
    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        application_id: uuid.UUID,
        loan_id: str,
        status: str,
        outcome_date: datetime,
        days_past_due: int = 0,
        default_status: str = "CURRENT",
        recovery_amount: float = 0,
        source: str = "CORE_BANKING",
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
        self.db.add(outcome)
        self.db.commit()
        self.db.refresh(outcome)
        return outcome
