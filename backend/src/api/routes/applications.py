from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies.permissions import require_permission
from src.audit.audit_service import AuditService
from src.core.database import get_db
from src.models.database import User
from src.schemas.application import ApplicationResponse, CreateApplicationRequest
from src.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(
    data: CreateApplicationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("applications:write")),
) -> Any:
    service = ApplicationService(db)
    app = service.create(user.institution_id, data)
    AuditService(db).record(
        user.institution_id,
        "APPLICATION_CREATED",
        "application",
        str(app.application_id),
        user.user_id,
    )
    return app


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("applications:read")),
) -> Any:
    return ApplicationService(db).list(user.institution_id, skip, limit)


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("applications:read")),
) -> Any:
    app = ApplicationService(db).get(application_id, user.institution_id)
    if not app:
        from src.core.exceptions import ResourceNotFoundError

        raise ResourceNotFoundError("Application", str(application_id))
    return app


@router.patch("/{application_id}/status")
def transition_status(
    application_id: uuid.UUID,
    new_status: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("applications:write")),
) -> dict[str, Any]:
    service = ApplicationService(db)
    app = service.transition(application_id, user.institution_id, new_status)
    AuditService(db).record(
        user.institution_id,
        "APPLICATION_UPDATED",
        "application",
        str(application_id),
        user.user_id,
        {"new_status": new_status},
    )
    return {"status": app.status}  # type: ignore[union-attr]
