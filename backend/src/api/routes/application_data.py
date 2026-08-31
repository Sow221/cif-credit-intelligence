"""Routes API d'ingestion des donnees de candidature (P0, etape 3).

Soumission des donnees brutes d'une application (SUBMIT APPLICATION DATA).
Multi-tenancy impose cote backend : institution issue du contexte authentifie.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.dependencies import CurrentUser, require_permission
from src.core.security import Permission
from src.db.session import get_db
from src.features.data_intake import DataIntakeService
from src.schemas.application_data import (
    ApplicationDataEntryResponse,
    ApplicationDataIngest,
    DataIngestSummary,
)

router = APIRouter(prefix="/v1/applications", tags=["application-data"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/{application_id}/data",
    response_model=DataIngestSummary,
    status_code=201,
)
def submit_application_data(
    application_id: uuid.UUID,
    payload: ApplicationDataIngest,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_UPDATE)),
) -> DataIngestSummary:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = DataIntakeService(db)
    return service.ingest(
        application_id=application_id,
        institution_id=uuid.UUID(current_user.institution_id),
        payload=payload,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )


@router.get(
    "/{application_id}/data",
    response_model=list[ApplicationDataEntryResponse],
)
def list_application_data(
    application_id: uuid.UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> list[ApplicationDataEntryResponse]:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = DataIntakeService(db)
    return service.list_for_application(
        application_id, uuid.UUID(current_user.institution_id)
    )
