"""Routes API des applications de credit (P0, etape 2).

Le multi-tenancy est impose cote backend : institution issue du contexte
authentifie. Le lifecycle (status) est distinct de la decision metier.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.dependencies import CurrentUser, require_permission
from src.core.security import Permission
from src.db.session import get_db
from src.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationStatus
from src.services.application_service import ApplicationService

router = APIRouter(prefix="/v1/applications", tags=["applications"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(
    payload: ApplicationCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_CREATE)),
) -> ApplicationResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ApplicationService(db)
    app = service.create_application(
        institution_id=uuid.UUID(current_user.institution_id),
        payload=payload,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )
    return ApplicationResponse.model_validate(app)


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> list[ApplicationResponse]:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ApplicationService(db)
    apps = service.list_applications(uuid.UUID(current_user.institution_id))
    return [ApplicationResponse.model_validate(a) for a in apps]


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: uuid.UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> ApplicationResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ApplicationService(db)
    app = service.get_application(
        application_id, uuid.UUID(current_user.institution_id)
    )
    return ApplicationResponse.model_validate(app)


@router.post("/{application_id}/transition", response_model=ApplicationResponse)
def transition_application(
    application_id: uuid.UUID,
    to_status: ApplicationStatus,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_UPDATE)),
) -> ApplicationResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ApplicationService(db)
    app = service.transition(
        application_id=application_id,
        institution_id=uuid.UUID(current_user.institution_id),
        to_status=to_status,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )
    return ApplicationResponse.model_validate(app)
