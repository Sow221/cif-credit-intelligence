from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.core.exceptions import InvalidStateTransitionError, ResourceNotFoundError
from src.models.database import Review

VALID_TRANSITIONS = {
    "PENDING": ["ASSIGNED"],
    "ASSIGNED": ["IN_PROGRESS"],
    "IN_PROGRESS": ["COMPLETED"],
}


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, application_id: uuid.UUID, decision_id: uuid.UUID, reason: str) -> Review:
        review = Review(
            application_id=application_id,
            decision_id=decision_id,
            status="PENDING",
            review_reason=reason,
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def assign(self, review_id: uuid.UUID, assigned_to: uuid.UUID) -> Review:
        review = self.db.query(Review).filter(Review.review_id == review_id).first()
        if not review:
            raise ResourceNotFoundError("Review", str(review_id))
        if "ASSIGNED" not in VALID_TRANSITIONS.get(review.status, []):
            raise InvalidStateTransitionError(review.status, "ASSIGNED")
        review.assigned_to = assigned_to
        review.status = "ASSIGNED"
        self.db.commit()
        self.db.refresh(review)
        return review

    def start(self, review_id: uuid.UUID) -> Review:
        review = self.db.query(Review).filter(Review.review_id == review_id).first()
        if not review:
            raise ResourceNotFoundError("Review", str(review_id))
        if "IN_PROGRESS" not in VALID_TRANSITIONS.get(review.status, []):
            raise InvalidStateTransitionError(review.status, "IN_PROGRESS")
        review.status = "IN_PROGRESS"
        review.started_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(review)
        return review

    def complete(self, review_id: uuid.UUID, final_action: str) -> Review:
        review = self.db.query(Review).filter(Review.review_id == review_id).first()
        if not review:
            raise ResourceNotFoundError("Review", str(review_id))
        if "COMPLETED" not in VALID_TRANSITIONS.get(review.status, []):
            raise InvalidStateTransitionError(review.status, "COMPLETED")
        review.status = "COMPLETED"
        review.final_action = final_action
        review.completed_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(review)
        return review

    def list_pending(self, institution_id: uuid.UUID) -> list[Review]:
        return (
            self.db.query(Review)
            .filter(Review.status.in_(["PENDING", "ASSIGNED", "IN_PROGRESS"]))
            .all()
        )
