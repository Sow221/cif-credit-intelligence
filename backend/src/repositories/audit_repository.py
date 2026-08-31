"""Repository de l'audit append-only (P0, etape 18).

Enregistre et lit les evenements d'audit dans audit_events. Aucune operation
de mise a jour ou suppression n'est exposee (append-only).
"""

import uuid
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import AuditEvent


class AuditRepository:
    """Acces append-only sur la table audit_events."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        event: str,
        institution_id: Optional[uuid.UUID],
        actor_id: Optional[str],
        entity_type: Optional[str],
        entity_id: Optional[str],
        request_id: Optional[str],
        details_json: Optional[Dict[str, Any]],
    ) -> AuditEvent:
        audit_event = AuditEvent(
            event=event,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            request_id=request_id,
            details_json=details_json,
        )
        self._db.add(audit_event)
        return audit_event

    def list(
        self,
        *,
        institution_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEvent]:
        query = select(AuditEvent).order_by(AuditEvent.created_at.desc())
        if institution_id is not None:
            query = query.where(AuditEvent.institution_id == institution_id)
        if entity_type is not None:
            query = query.where(AuditEvent.entity_type == entity_type)
        if entity_id is not None:
            query = query.where(AuditEvent.entity_id == entity_id)
        return list(
            self._db.execute(query.offset(offset).limit(limit)).scalars().all()
        )
