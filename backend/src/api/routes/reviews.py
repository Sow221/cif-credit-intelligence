from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies.permissions import require_permission
from src.audit.audit_service import AuditService
from src.core.database import get_db
from src.models.database import User
from src.schemas.review import AssignReviewRequest, CompleteReviewRequest, ReviewResponse
from src.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewResponse])
def list_reviews(
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("reviews:read")),
) -> list[ReviewResponse]:
    service = ReviewService(db)
    reviews = service.list_pending(user.institution_id)
    return [
        ReviewResponse(
            review_id=str(r.review_id),
            application_id=str(r.application_id),
            assigned_to=str(r.assigned_to) if r.assigned_to else None,
            status=r.status,
            review_reason=r.review_reason,
            final_action=r.final_action,
            started_at=str(r.started_at) if r.started_at else None,
            completed_at=str(r.completed_at) if r.completed_at else None,
        )
        for r in reviews
    ]


@router.patch("/{review_id}/assign", response_model=ReviewResponse)
def assign_review(
    review_id: uuid.UUID,
    data: AssignReviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("reviews:write")),
) -> ReviewResponse:
    service = ReviewService(db)
    review = service.assign(review_id, data.assigned_to)
    AuditService(db).record(
        user.institution_id, "REVIEW_STARTED", "review", str(review_id), user.user_id
    )
    return ReviewResponse(
        review_id=str(review.review_id),
        application_id=str(review.application_id),
        assigned_to=str(review.assigned_to),
        status=review.status,
        review_reason=review.review_reason,
    )


@router.patch("/{review_id}/start")
def start_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("reviews:write")),
) -> dict[str, Any]:
    service = ReviewService(db)
    review = service.start(review_id)
    return {"status": review.status}


@router.patch("/{review_id}/complete")
def complete_review(
    review_id: uuid.UUID,
    data: CompleteReviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("reviews:write")),
) -> dict[str, Any]:
    service = ReviewService(db)
    review = service.complete(review_id, data.final_action)
    AuditService(db).record(
        user.institution_id,
        "REVIEW_COMPLETED",
        "review",
        str(review_id),
        user.user_id,
        {"final_action": data.final_action},
    )
    return {"status": review.status, "final_action": review.final_action}
