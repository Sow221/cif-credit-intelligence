from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.models.database import Application, Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs: Any) -> Review:
        obj = Review(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, id: uuid.UUID) -> Review | None:
        return self.db.query(Review).filter(Review.review_id == id).first()

    def get_multi(
        self,
        institution_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Review]:
        return (
            self.db.query(Review)
            .join(Application, Review.application_id == Application.application_id)
            .filter(Application.institution_id == institution_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_application(
        self,
        application_id: uuid.UUID,
    ) -> Review | None:
        return self.db.query(Review).filter(Review.application_id == application_id).first()

    def get_by_status(
        self,
        status: str,
        institution_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Review]:
        return (
            self.db.query(Review)
            .join(Application, Review.application_id == Application.application_id)
            .filter(
                Application.institution_id == institution_id,
                Review.status == status,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def assign(
        self,
        review_id: uuid.UUID,
        assigned_to: uuid.UUID,
    ) -> Review | None:
        obj = self.get_by_id(review_id)
        if obj is None or obj.status != "PENDING":
            return None
        obj.assigned_to = assigned_to
        obj.status = "ASSIGNED"
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def start_review(self, review_id: uuid.UUID) -> Review | None:
        obj = self.get_by_id(review_id)
        if obj is None or obj.status != "ASSIGNED":
            return None
        obj.status = "IN_PROGRESS"
        obj.started_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def complete_review(
        self,
        review_id: uuid.UUID,
        final_action: str,
    ) -> Review | None:
        obj = self.get_by_id(review_id)
        if obj is None or obj.status != "IN_PROGRESS":
            return None
        obj.status = "COMPLETED"
        obj.final_action = final_action
        obj.completed_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: uuid.UUID, **kwargs: Any) -> Review | None:
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
