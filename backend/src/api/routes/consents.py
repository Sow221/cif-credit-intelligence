"""Routes API de gestion du consentement (P0, etape 6).

Multi-tenancy impose cote backend : institution issue du contexte authentifie,
jamais du corps de requete.
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from src.api.dependencies import CurrentUser, require_permission
from src.core.security import Permission
from src.db.session import get_db
from src.governance.consent import ConsentGuard, ConsentService
from src.repositories.consent_repository import ConsentRepository
from src.repositories.client_repository import ClientRepository
from src.schemas.consent import (
    ConsentCheckResponse,
    ConsentCreate,
    ConsentResponse,
)

router = APIRouter(prefix="/v1/consents", tags=["consents"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ConsentResponse, status_code=201)
def create_consent(
    payload: ConsentCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.CONSENT_MANAGE)),
) -> ConsentResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    institution_id = uuid.UUID(current_user.institution_id)

    # Le client doit appartenir au tenant.
    client = ClientRepository(db).get(payload.client_id, institution_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client introuvable")

    consent = ConsentService(db).record(
        client_id=payload.client_id,
        institution_id=institution_id,
        status=payload.status,
        purpose=payload.purpose,
        source_id=payload.source_id,
        version=payload.version,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )
    return ConsentResponse.model_validate(consent)


@router.get("", response_model=list[ConsentResponse])
def list_consents(
    client_id: uuid.UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.CONSENT_MANAGE)),
) -> list[ConsentResponse]:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    institution_id = uuid.UUID(current_user.institution_id)
    consents = ConsentRepository(db).list_for_client(client_id, institution_id)
    return [ConsentResponse.model_validate(c) for c in consents]


@router.get("/check", response_model=ConsentCheckResponse)
def check_consent(
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.CONSENT_MANAGE)),
    client_id: uuid.UUID = Query(...),
    source_id: Optional[uuid.UUID] = None,
    purpose: Optional[str] = Query(None, max_length=200),
) -> ConsentCheckResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    institution_id = uuid.UUID(current_user.institution_id)
    # Le client doit appartenir au tenant (multi-tenancy).
    if ClientRepository(db).get(client_id, institution_id) is None:
        raise HTTPException(status_code=404, detail="Client introuvable")
    check = ConsentGuard(db).check(
        client_id=client_id,
        institution_id=institution_id,
        source_id=source_id,
        purpose=purpose,
    )
    return ConsentCheckResponse(**check.model_dump())
