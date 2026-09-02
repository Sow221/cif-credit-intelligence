"""Routes API des loan outcomes (P0, etape 18 / 36)."""

import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.dependencies import CurrentUser, require_permission
from src.core.security import Permission
from src.db.session import get_db
from src.repositories.loan_outcome_repository import LoanOutcomeRepository
from src.schemas.outcome import OutcomeCreate, OutcomeResponse
from src.services.outcome_service import OutcomeService

router = APIRouter(prefix="/v1/applications", tags=["outcomes"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/{application_id}/outcomes", response_model=OutcomeResponse, status_code=201)
def create_outcome(
    application_id: uuid.UUID,
    payload: OutcomeCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> OutcomeResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    if payload.application_id != application_id:
        raise HTTPException(status_code=400, detail="application_id incoherent")
    service = OutcomeService(db)
    outcome = service.create_outcome(
        application_id=application_id,
        institution_id=uuid.UUID(current_user.institution_id),
        loan_id=payload.loan_id,
        status=payload.status,
        outcome_date=payload.outcome_date,
        days_past_due=payload.days_past_due,
        default_status=payload.default_status,
        recovery_amount=payload.recovery_amount,
        source=payload.source,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )
    return outcome


@router.get("/{application_id}/outcomes", response_model=List[OutcomeResponse])
def list_outcomes(
    application_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> List[OutcomeResponse]:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    repo = LoanOutcomeRepository(db)
    return repo.list_for_application(application_id, uuid.UUID(current_user.institution_id))