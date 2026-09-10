from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.models.database import Application, LoanOutcome


class OutcomeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs: Any) -> LoanOutcome:
        obj = LoanOutcome(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, id: uuid.UUID) -> LoanOutcome | None:
        return self.db.query(LoanOutcome).filter(LoanOutcome.outcome_id == id).first()

    def get_multi(
        self,
        institution_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LoanOutcome]:
        return (
            self.db.query(LoanOutcome)
            .join(Application, LoanOutcome.application_id == Application.application_id)
            .filter(Application.institution_id == institution_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_application(
        self,
        application_id: uuid.UUID,
    ) -> LoanOutcome | None:
        return (
            self.db.query(LoanOutcome).filter(LoanOutcome.application_id == application_id).first()
        )

    def update(self, id: uuid.UUID, **kwargs: Any) -> LoanOutcome | None:
        obj = self.get_by_id(id)
        if obj is None:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: uuid.UUID) -> bool:
        obj = self.get_by_id(id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
