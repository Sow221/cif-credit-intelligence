"""Repository du client (P0, etape 1).

Encapsule les acces PostgreSQL sur la table clients. Toutes les operations
sont scopees par institution_id (multi-tenancy).
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Client


class ClientRepository:
    """Acces CRUD sur l'entite Client, scope tenant."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, institution_id: uuid.UUID, **fields) -> Client:
        client = Client(institution_id=institution_id, **fields)
        self._db.add(client)
        return client

    def get(
        self, client_id: uuid.UUID, institution_id: uuid.UUID
    ) -> Optional[Client]:
        return (
            self._db.execute(
                select(Client).where(
                    Client.client_id == client_id,
                    Client.institution_id == institution_id,
                )
            )
            .scalars()
            .first()
        )

    def list(self, institution_id: uuid.UUID) -> list[Client]:
        return list(
            self._db.execute(
                select(Client)
                .where(Client.institution_id == institution_id)
                .order_by(Client.created_at.desc())
            )
            .scalars()
            .all()
        )

    def update(self, client: Client, **fields) -> Client:
        for key, value in fields.items():
            if value is not None:
                setattr(client, key, value)
        return client
