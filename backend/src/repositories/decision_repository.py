from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.models.database import Decision


class DecisionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs: Any) -> Decision:
        obj = Decision(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, id: uuid.UUID) -> Decision | None:
        return self.db.query(Decision).filter(Decision.decision_id == id).first()

    def get_multi(
        self,
        institution_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Decision]:
        return (
            self.db.query(Decision)
            .filter(Decision.institution_id == institution_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_application(
        self,
        application_id: uuid.UUID,
    ) -> Decision | None:
        return self.db.query(Decision).filter(Decision.application_id == application_id).first()

    def update(
        self,
        id: uuid.UUID,
        institution_id: uuid.UUID | None = None,
        **kwargs: Any,
    ) -> Decision | None:
        query = self.db.query(Decision).filter(Decision.decision_id == id)
        if institution_id is not None:
            query = query.filter(Decision.institution_id == institution_id)
        obj = query.first()
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
