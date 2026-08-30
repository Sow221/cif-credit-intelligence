"""Routes de consultation et d'override des decisions.

Endpoints :
- GET  /v1/decisions            -> liste paginee des decisions
- GET  /v1/decisions/{id}       -> detail d'une decision
- POST /v1/decisions/{id}/override -> override humain (journal audite)
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from src.api.middleware.rate_limit import get_limit, limiter
from src.api.schemas.request import OverrideRequest
from src.api.schemas.response import (
    DecisionItem,
    DecisionListResponse,
)
from src.config.settings import Settings
from src.db.models import AuditLog, Prediction
from src.db.session import get_db

router = APIRouter(tags=["decisions"])

settings = Settings()

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/v1/decisions",
    response_model=DecisionListResponse,
)
@limiter.limit(get_limit("rate_decisions"))
async def list_decisions(
    request: Request,
    db: DbSession,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> DecisionListResponse:
    """Liste des decisions (recommandations) les plus recentes."""
    decisions = (
        db.query(Prediction)
        .order_by(Prediction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return DecisionListResponse(
        total=len(decisions), items=[DecisionItem.model_validate(d) for d in decisions]
    )


@router.get(
    "/v1/decisions/{prediction_id}",
    response_model=DecisionItem,
)
@limiter.limit(get_limit("rate_decisions"))
async def get_decision(prediction_id: UUID, request: Request, db: DbSession) -> DecisionItem:
    """Detail d'une decision par son identifiant de prediction."""
    decision = (
        db.query(Prediction).filter(Prediction.prediction_id == prediction_id).first()
    )
    if not decision:
        raise HTTPException(status_code=404, detail="Decision non trouvee")
    return DecisionItem.model_validate(decision)


@router.post(
    "/v1/decisions/{prediction_id}/override",
    response_model=dict,
)
@limiter.limit(get_limit("rate_override"))
async def override_decision(
    prediction_id: UUID,
    body: OverrideRequest,
    request: Request,
    db: DbSession,
) -> dict:
    """Override humain d'une decision : l'entree est journalisee en audit."""
    decision = (
        db.query(Prediction).filter(Prediction.prediction_id == prediction_id).first()
    )
    if not decision:
        raise HTTPException(status_code=404, detail="Decision non trouvee")

    audit = AuditLog(
        prediction_id=prediction_id,
        agent_id=body.agent_id,
        agent_decision=body.decision,
        agent_justification=body.justification,
        is_override=True,
    )
    db.add(audit)
    db.commit()
    return {"status": "success", "audit_id": str(audit.audit_id)}