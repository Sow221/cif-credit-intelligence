from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.models.database import Client


class ClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs: Any) -> Client:
        obj = Client(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(
        self,
        id: uuid.UUID,
        institution_id: uuid.UUID | None = None,
    ) -> Client | None:
        query = self.db.query(Client).filter(Client.client_id == id)
        if institution_id is not None:
            query = query.filter(Client.institution_id == institution_id)
        return query.first()

    def get_multi(
        self,
        institution_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Client]:
        return (
            self.db.query(Client)
            .filter(Client.institution_id == institution_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, id: uuid.UUID, **kwargs: Any) -> Client | None:
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
