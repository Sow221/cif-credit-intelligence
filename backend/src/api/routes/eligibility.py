"""Routes API d'eligibilite (P0, etape 4).

Repond a la question ELIGIBLE ? avant le risque et la decision.
Multi-tenancy impose cote backend ; les regles restent configurables.
"""

import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.api.dependencies import CurrentUser, require_permission
from src.core.security import Permission
from src.db.session import get_db
from src.repositories.application_repository import ApplicationRepository
from src.repositories.client_repository import ClientRepository
from src.schemas.eligibility import EligibilityInput, EligibilityResult, EligibilityRules
from src.services.eligibility_service import EligibilityService

router = APIRouter(prefix="/v1/applications", tags=["eligibility"])

DbSession = Annotated[Session, Depends(get_db)]


def _compute_age(date_of_birth: Optional[datetime]) -> Optional[float]:
    if date_of_birth is None:
        return None
    today = datetime.utcnow()
    return (today - date_of_birth).days / 365.25


@router.post("/{application_id}/eligibility", response_model=EligibilityResult)
def check_eligibility(
    application_id: uuid.UUID,
    request: Request,
    db: DbSession,
    rules: Optional[EligibilityRules] = Body(None),
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> EligibilityResult:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    institution_id = uuid.UUID(current_user.institution_id)

    application = ApplicationRepository(db).get(application_id, institution_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application introuvable")

    client = ClientRepository(db).get(application.client_id, institution_id)
    age = _compute_age(client.date_of_birth) if client else None

    result = EligibilityService().evaluate(
        EligibilityInput(
            client_age=age,
            requested_amount=application.requested_amount,
            currency=application.currency,
            requested_term=application.requested_term,
            product_id=application.product_id,
        ),
        rules=rules,
    )

    AuditService(db).log(
        AuditEventType.ELIGIBILITY_CHECKED,
        institution_id=institution_id,
        actor_id=current_user.subject,
        entity_type="application",
        entity_id=str(application_id),
        request_id=getattr(request.state, "request_id", None),
        details={"status": result.status.value, "rules_version": result.rules_version},
    )
    db.commit()
    return result
