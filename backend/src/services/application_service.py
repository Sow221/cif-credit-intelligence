from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from src.models.database import Application
from src.repositories.application_repository import ApplicationRepository
from src.schemas.application import CreateApplicationRequest

VALID_TRANSITIONS = {
    "DRAFT": ["SUBMITTED", "CANCELLED"],
    "SUBMITTED": ["DATA_VALIDATION", "CANCELLED"],
    "DATA_VALIDATION": ["PROFILED", "CANCELLED"],
    "PROFILED": ["SCORED", "CANCELLED"],
    "SCORED": ["REVIEW", "DECIDED", "CANCELLED"],
    "REVIEW": ["DECIDED", "CANCELLED"],
    "DECIDED": ["DISBURSED", "CANCELLED"],
}


class ApplicationService:
    def __init__(self, db: Session):
        self.repo = ApplicationRepository(db)

    def create(self, institution_id: uuid.UUID, data: CreateApplicationRequest) -> Application:
        return self.repo.create(institution_id=institution_id, status="DRAFT", **data.model_dump())

    def get(self, application_id: uuid.UUID, institution_id: uuid.UUID) -> Application | None:
        return self.repo.get_by_id(application_id, institution_id)

    def list(self, institution_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Application]:
        return self.repo.get_multi(institution_id, skip, limit)

    def transition(
        self, application_id: uuid.UUID, institution_id: uuid.UUID, new_status: str
    ) -> Application | None:
        app = self.repo.get_by_id(application_id, institution_id)
        if not app:
            raise ValueError("Application introuvable")
        allowed = VALID_TRANSITIONS.get(app.status, [])
        if new_status not in allowed:
            raise ValueError(f"Transition invalide: {app.status} → {new_status}")
        return self.repo.update_status(app.application_id, institution_id, new_status)
