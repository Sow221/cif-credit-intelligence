"""Routes API de la revue humaine (P0, etape 16).

Une application REVIEW apparait dans une file de revue. Endpoints :
POST /v1/reviews, GET /v1/reviews, PATCH /v1/reviews/{id}/assign,
POST /v1/reviews/{id}/start, POST /v1/reviews/{id}/complete
"""

import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.dependencies import CurrentUser, require_permission
from src.core.security import Permission
from src.db.session import get_db
from src.schemas.review import ReviewAssign, ReviewComplete, ReviewCreate, ReviewResponse
from src.services.review_service import ReviewService

router = APIRouter(prefix="/v1/reviews", tags=["reviews"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ReviewResponse, status_code=201)
def create_review(
    payload: ReviewCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> ReviewResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ReviewService(db)
    review = service.create_review(
        application_id=payload.application_id,
        institution_id=uuid.UUID(current_user.institution_id),
        review_reason=payload.review_reason,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )
    return review


@router.get("", response_model=List[ReviewResponse])
def list_reviews(
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> List[ReviewResponse]:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    from src.repositories.review_repository import ReviewRepository

    repo = ReviewRepository(db)
    return repo.list_queue(uuid.UUID(current_user.institution_id))


@router.patch("/{review_id}/assign", response_model=ReviewResponse)
def assign_review(
    review_id: uuid.UUID,
    payload: ReviewAssign,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> ReviewResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ReviewService(db)
    return service.assign_review(
        review_id=review_id,
        institution_id=uuid.UUID(current_user.institution_id),
        assigned_to=payload.assigned_to,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("/{review_id}/start", response_model=ReviewResponse)
def start_review(
    review_id: uuid.UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> ReviewResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    from src.repositories.review_repository import ReviewRepository

    repo = ReviewRepository(db)
    review = repo.get(review_id, uuid.UUID(current_user.institution_id))
    if review is None:
        raise HTTPException(status_code=404, detail="Review introuvable")
    repo.start(review)
    db.commit()
    return review


@router.post("/{review_id}/complete", response_model=ReviewResponse)
def complete_review(
    review_id: uuid.UUID,
    payload: ReviewComplete,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> ReviewResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ReviewService(db)
    return service.complete_review(
        review_id=review_id,
        institution_id=uuid.UUID(current_user.institution_id),
        final_action=payload.final_action,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )