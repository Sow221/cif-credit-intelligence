from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.models.database import AuditEvent


class AuditRepository:
    """Append-only repository for audit events.

    Provides create and read methods only.
    Updates and deletes are intentionally omitted to preserve the audit trail.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs: Any) -> AuditEvent:
        obj = AuditEvent(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, id: uuid.UUID) -> AuditEvent | None:
        return self.db.query(AuditEvent).filter(AuditEvent.event_id == id).first()

    def get_multi(
        self,
        institution_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditEvent]:
        return (
            self.db.query(AuditEvent)
            .filter(AuditEvent.institution_id == institution_id)
            .order_by(AuditEvent.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_entity(
        self,
        institution_id: uuid.UUID,
        entity_type: str,
        entity_id: str,
    ) -> list[AuditEvent]:
        return (
            self.db.query(AuditEvent)
            .filter(
                AuditEvent.institution_id == institution_id,
                AuditEvent.entity_type == entity_type,
                AuditEvent.entity_id == entity_id,
            )
            .order_by(AuditEvent.created_at.desc())
            .all()
        )

    def get_by_event_type(
        self,
        institution_id: uuid.UUID,
        event_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditEvent]:
        return (
            self.db.query(AuditEvent)
            .filter(
                AuditEvent.institution_id == institution_id,
                AuditEvent.event_type == event_type,
            )
            .order_by(AuditEvent.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
