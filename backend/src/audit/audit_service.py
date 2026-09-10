from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.models.database import AuditEvent


class AuditService:
    EVENT_TYPES = {
        "APPLICATION_CREATED",
        "APPLICATION_UPDATED",
        "DATA_RECEIVED",
        "DATA_VALIDATED",
        "CONSENT_CREATED",
        "CONSENT_CHANGED",
        "PROFILE_CREATED",
        "FEATURE_SNAPSHOT_CREATED",
        "SCORE_CREATED",
        "UNCERTAINTY_CREATED",
        "DECISION_RECOMMENDED",
        "REVIEW_STARTED",
        "REVIEW_COMPLETED",
        "DECISION_MADE",
        "OVERRIDE_CREATED",
        "OUTCOME_RECEIVED",
        "MODEL_CREATED",
        "MODEL_VALIDATED",
        "MODEL_PROMOTED",
        "MODEL_RETIRED",
        "POLICY_CREATED",
        "POLICY_CHANGED",
        "CONFIG_CHANGED",
        "LOGIN",
        "LOGOUT",
        "ACCESS_DENIED",
    }

    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        institution_id: uuid.UUID,
        event_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor_id: uuid.UUID | None = None,
        details: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> AuditEvent:
        payload_hash = None
        if payload:
            payload_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True, default=str).encode()
            ).hexdigest()
        event = AuditEvent(
            institution_id=institution_id,
            actor_id=actor_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details_json=json.dumps(details, default=str) if details else None,
            payload_hash=payload_hash,
            request_id=request_id,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_events(
        self,
        institution_id: uuid.UUID,
        event_type: str | None = None,
        entity_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        query = self.db.query(AuditEvent).filter(AuditEvent.institution_id == institution_id)
        if event_type:
            query = query.filter(AuditEvent.event_type == event_type)
        if entity_type:
            query = query.filter(AuditEvent.entity_type == entity_type)
        return query.order_by(AuditEvent.created_at.desc()).limit(limit).all()
