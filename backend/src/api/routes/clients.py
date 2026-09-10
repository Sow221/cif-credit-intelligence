from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies.permissions import require_permission
from src.audit.audit_service import AuditService
from src.core.database import get_db
from src.models.database import User
from src.schemas.client import ClientResponse, CreateClientRequest
from src.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientResponse, status_code=201)
def create_client(
    data: CreateClientRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("clients:write")),
) -> Any:
    service = ClientService(db)
    client = service.create(user.institution_id, data)
    AuditService(db).record(
        user.institution_id, "APPLICATION_CREATED", "client", str(client.client_id), user.user_id
    )
    return client


@router.get("", response_model=list[ClientResponse])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("clients:read")),
) -> Any:
    return ClientService(db).list(user.institution_id, skip, limit)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("clients:read")),
) -> Any:
    client = ClientService(db).get(client_id, user.institution_id)
    if not client:
        from src.core.exceptions import ResourceNotFoundError

        raise ResourceNotFoundError("Client", str(client_id))
    return client
