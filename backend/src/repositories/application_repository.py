from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.models.database import Application


class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs: Any) -> Application:
        obj = Application(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(
        self,
        id: uuid.UUID,
        institution_id: uuid.UUID | None = None,
    ) -> Application | None:
        query = self.db.query(Application).filter(Application.application_id == id)
        if institution_id is not None:
            query = query.filter(Application.institution_id == institution_id)
        return query.first()

    def get_multi(
        self,
        institution_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[Application]:
        query = self.db.query(Application).filter(Application.institution_id == institution_id)
        if status is not None:
            query = query.filter(Application.status == status)
        return query.offset(skip).limit(limit).all()

    def update_status(
        self,
        id: uuid.UUID,
        institution_id: uuid.UUID,
        new_status: str,
    ) -> Application | None:
        obj = self.get_by_id(id, institution_id=institution_id)
        if obj is None:
            return None
        obj.status = new_status
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: uuid.UUID, **kwargs: Any) -> Application | None:
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
