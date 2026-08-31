"""Service client (P0, etape 1).

Orchestre la logique metier du client : creation, lecture, liste, mise a
jour. Applique le scope institution (multi-tenancy) et journalise l'audit.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.core.exceptions import NotFoundError
from src.db.models import Client
from src.repositories.client_repository import ClientRepository
from src.schemas.client import ClientCreate, ClientUpdate


class ClientService:
    """Logique metier du client."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ClientRepository(db)
        self._audit = AuditService(db)

    def create_client(
        self,
        *,
        institution_id: uuid.UUID,
        payload: ClientCreate,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Client:
        fields = payload.model_dump(exclude_none=True)
        status = fields.pop("status", "ACTIVE")
        client = self._repo.create(institution_id=institution_id, **fields)
        client.status = status
        self._db.flush()
        self._audit.log(
            AuditEventType.CLIENT_CREATED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="client",
            entity_id=str(client.client_id),
            request_id=request_id,
            details={"status": client.status},
        )
        self._db.commit()
        self._db.refresh(client)
        return client

    def get_client(
        self, client_id: uuid.UUID, institution_id: uuid.UUID
    ) -> Client:
        client = self._repo.get(client_id, institution_id)
        if client is None:
            raise NotFoundError(f"Client {client_id} introuvable")
        return client

    def list_clients(self, institution_id: uuid.UUID) -> list[Client]:
        return self._repo.list(institution_id)

    def update_client(
        self,
        *,
        client_id: uuid.UUID,
        institution_id: uuid.UUID,
        payload: ClientUpdate,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Client:
        client = self.get_client(client_id, institution_id)
        fields = payload.model_dump(exclude_none=True)
        self._repo.update(client, **fields)
        self._db.flush()
        self._audit.log(
            AuditEventType.APPLICATION_UPDATED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="client",
            entity_id=str(client.client_id),
            request_id=request_id,
            details={"updated_fields": list(fields.keys())},
        )
        self._db.commit()
        self._db.refresh(client)
        return client
