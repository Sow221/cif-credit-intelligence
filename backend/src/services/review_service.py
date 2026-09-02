"""Review service (P0, etape 16).

Une application dont la decision est REVIEW doit apparaitre dans une file de
revue. Le service orchestre creation, assignation et cloture de la revue.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.core.exceptions import NotFoundError
from src.db.models import Review
from src.repositories.application_repository import ApplicationRepository
from src.repositories.review_repository import ReviewRepository


class ReviewService:
    """Orchestration de la file de revue humaine."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._reviews = ReviewRepository(db)
        self._apps = ApplicationRepository(db)
        self._audit = AuditService(db)

    def create_review(
        self,
        *,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        review_reason: str,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Review:
        app = self._apps.get(application_id, institution_id)
        if app is None:
            raise NotFoundError(f"Application {application_id} introuvable")
        review = self._reviews.create(application_id=application_id, review_reason=review_reason)
        self._db.flush()
        self._audit.log(
            AuditEventType.REVIEW_STARTED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="review",
            entity_id=str(review.review_id),
            request_id=request_id,
            details={"application_id": str(application_id), "review_reason": review_reason},
        )
        self._db.commit()
        return review

    def assign_review(
        self,
        *,
        review_id: uuid.UUID,
        institution_id: uuid.UUID,
        assigned_to: str,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Review:
        review = self._reviews.get(review_id, institution_id)
        if review is None:
            raise NotFoundError(f"Review {review_id} introuvable")
        self._reviews.assign(review, assigned_to)
        self._db.commit()
        return review

    def complete_review(
        self,
        *,
        review_id: uuid.UUID,
        institution_id: uuid.UUID,
        final_action: str,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Review:
        review = self._reviews.get(review_id, institution_id)
        if review is None:
            raise NotFoundError(f"Review {review_id} introuvable")
        self._reviews.complete(review, final_action)
        self._db.flush()
        self._audit.log(
            AuditEventType.REVIEW_COMPLETED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="review",
            entity_id=str(review.review_id),
            request_id=request_id,
            details={"final_action": final_action},
        )
        self._db.commit()
        return review