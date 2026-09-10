from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies.permissions import require_permission
from src.audit.audit_service import AuditService
from src.core.database import get_db
from src.core.exceptions import (
    InvalidStateTransitionError,
    OverrideReasonRequiredError,
    ResourceNotFoundError,
)
from src.models.database import Decision, User
from src.schemas.decision import (
    DecisionRequest,
    DecisionResponse,
    OverrideRequest,
    OverrideResponse,
)
from src.services.decision_engine import DecisionEngine, DecisionInput

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.post("", response_model=DecisionResponse, status_code=201)
def make_decision(
    data: DecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("decisions:read")),
) -> DecisionResponse:
    engine = DecisionEngine()
    inputs = DecisionInput(
        eligible=True,
        pd_calibrated=0.5,
        uncertainty_level="LOW",
        information_state="FULL_FILE",
        data_quality="PASS",
        policy={"approve_threshold": 0.7, "decline_threshold": 0.3},
    )
    result = engine.decide(inputs)
    decision = Decision(
        application_id=data.application_id,
        institution_id=user.institution_id,
        policy_id=uuid.uuid4(),
        prediction_id=uuid.uuid4(),
        recommendation=result.recommendation,
        decision_reason=result.reason,
        actor_id=user.user_id,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    AuditService(db).record(
        user.institution_id,
        "DECISION_MADE",
        "decision",
        str(decision.decision_id),
        user.user_id,
        {"recommendation": result.recommendation},
    )
    return DecisionResponse(
        decision_id=str(decision.decision_id),
        application_id=str(data.application_id),
        recommendation=result.recommendation,
        decision_reason=result.reason,
    )


@router.post("/{decision_id}/override", response_model=OverrideResponse, status_code=201)
def override_decision(
    decision_id: uuid.UUID,
    data: OverrideRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("decisions:override")),
) -> OverrideResponse:
    decision = db.query(Decision).filter(Decision.decision_id == decision_id).first()
    if not decision:
        raise ResourceNotFoundError("Decision", str(decision_id))
    if not data.override_reason or not data.override_reason.strip():
        raise OverrideReasonRequiredError()
    if decision.final_decision:
        raise InvalidStateTransitionError(decision.recommendation, "OVERRIDE")
    decision.final_decision = data.final_decision
    decision.actor_id = user.user_id
    db.commit()
    AuditService(db).record(
        user.institution_id,
        "OVERRIDE_CREATED",
        "decision",
        str(decision_id),
        user.user_id,
        {"original": decision.recommendation, "final": data.final_decision},
    )
    return OverrideResponse(
        override_id=str(uuid.uuid4()),
        decision_id=str(decision_id),
        original_recommendation=decision.recommendation,
        final_decision=data.final_decision,
        override_reason=data.override_reason,
        actor_id=str(user.user_id),
        created_at=str(decision.created_at),
    )
