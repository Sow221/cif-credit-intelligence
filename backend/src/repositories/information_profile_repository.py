from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.models.database import InformationProfile


class InformationProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs: Any) -> InformationProfile:
        obj = InformationProfile(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, id: uuid.UUID) -> InformationProfile | None:
        return self.db.query(InformationProfile).filter(InformationProfile.profile_id == id).first()

    def get_multi(
        self,
        institution_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[InformationProfile]:
        return (
            self.db.query(InformationProfile)
            .filter(InformationProfile.institution_id == institution_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_application(
        self,
        application_id: uuid.UUID,
    ) -> InformationProfile | None:
        return (
            self.db.query(InformationProfile)
            .filter(InformationProfile.application_id == application_id)
            .first()
        )

    def update(self, id: uuid.UUID, **kwargs: Any) -> InformationProfile | None:
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
