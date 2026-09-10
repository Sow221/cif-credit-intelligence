from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from src.models.database import Client
from src.repositories.client_repository import ClientRepository
from src.schemas.client import CreateClientRequest


class ClientService:
    def __init__(self, db: Session):
        self.repo = ClientRepository(db)

    def create(self, institution_id: uuid.UUID, data: CreateClientRequest) -> Client:
        return self.repo.create(institution_id=institution_id, **data.model_dump())

    def get(self, client_id: uuid.UUID, institution_id: uuid.UUID) -> Client | None:
        return self.repo.get_by_id(client_id, institution_id)

    def list(self, institution_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Client]:
        return self.repo.get_multi(institution_id, skip, limit)
