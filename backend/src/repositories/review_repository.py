"""Repository des revues humaines (P0, etape 16).

La table reviews est rattachee a applications ; le scope tenant est applique
par jointure avec applications (multi-tenancy).
"""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Application, Review


class ReviewRepository:
    """Acces persistant a la file de revue."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        application_id: uuid.UUID,
        review_reason: Optional[str],
    ) -> Review:
        review = Review(
            application_id=application_id,
            review_reason=review_reason,
            status="PENDING",
        )
        self._db.add(review)
        return review

    def get(self, review_id: uuid.UUID, institution_id: uuid.UUID) -> Optional[Review]:
        stmt = (
            select(Review)
            .join(Application, Application.application_id == Review.application_id)
            .where(Review.review_id == review_id, Application.institution_id == institution_id)
        )
        return self._db.scalar(stmt)

    def list_queue(self, institution_id: uuid.UUID, status: str = "PENDING") -> List[Review]:
        stmt = (
            select(Review)
            .join(Application, Application.application_id == Review.application_id)
            .where(Application.institution_id == institution_id, Review.status == status)
            .order_by(Review.review_id.asc())
        )
        return list(self._db.scalars(stmt).all())

    def assign(self, review: Review, assigned_to: str) -> Review:
        review.assigned_to = assigned_to
        review.status = "ASSIGNED"
        return review

    def start(self, review: Review) -> Review:
        from datetime import datetime, timezone

        review.status = "IN_PROGRESS"
        review.started_at = datetime.now(timezone.utc)
        return review

    def complete(self, review: Review, final_action: str) -> Review:
        from datetime import datetime, timezone

        review.final_action = final_action
        review.status = "COMPLETED"
        review.completed_at = datetime.now(timezone.utc)
        return review