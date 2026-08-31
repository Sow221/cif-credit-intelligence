"""Routes API du client (P0, etape 1).

Le multi-tenancy est impose cote backend : l'institution provient du
contexte authentifie (CurrentUser), jamais du corps de requete.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.dependencies import CurrentUser, get_current_user, require_permission
from src.core.security import Permission
from src.db.session import get_db
from src.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from src.services.client_service import ClientService

router = APIRouter(prefix="/v1/clients", tags=["clients"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ClientResponse, status_code=201)
def create_client(
    payload: ClientCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.CLIENT_CREATE)),
) -> ClientResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ClientService(db)
    client = service.create_client(
        institution_id=uuid.UUID(current_user.institution_id),
        payload=payload,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )
    return ClientResponse.model_validate(client)


@router.get("", response_model=list[ClientResponse])
def list_clients(
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.CLIENT_READ)),
) -> list[ClientResponse]:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ClientService(db)
    clients = service.list_clients(uuid.UUID(current_user.institution_id))
    return [ClientResponse.model_validate(c) for c in clients]


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: uuid.UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.CLIENT_READ)),
) -> ClientResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ClientService(db)
    client = service.get_client(
        client_id, uuid.UUID(current_user.institution_id)
    )
    return ClientResponse.model_validate(client)


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: uuid.UUID,
    payload: ClientUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.CLIENT_UPDATE)),
) -> ClientResponse:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = ClientService(db)
    client = service.update_client(
        client_id=client_id,
        institution_id=uuid.UUID(current_user.institution_id),
        payload=payload,
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )
    return ClientResponse.model_validate(client)
