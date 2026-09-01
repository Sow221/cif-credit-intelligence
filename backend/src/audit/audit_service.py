"""Service d'audit append-only (P0, etape 18).

Enregistre chaque evenement dans la table audit_events. Les evenements sont
en append-only : aucune modification ni suppression d'evenements historiques.

Evenements minimum requis (consigne section 34).
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from src.db.models import AuditEvent
from src.repositories.audit_repository import AuditRepository


class AuditEventType(str, Enum):
    APPLICATION_CREATED = "APPLICATION_CREATED"
    APPLICATION_UPDATED = "APPLICATION_UPDATED"
    DATA_RECEIVED = "DATA_RECEIVED"
    DATA_VALIDATED = "DATA_VALIDATED"
    CONSENT_CREATED = "CONSENT_CREATED"
    CONSENT_CHANGED = "CONSENT_CHANGED"
    PROFILE_CREATED = "PROFILE_CREATED"
    FEATURE_SNAPSHOT_CREATED = "FEATURE_SNAPSHOT_CREATED"
    SCORE_CREATED = "SCORE_CREATED"
    UNCERTAINTY_CREATED = "UNCERTAINTY_CREATED"
    DECISION_RECOMMENDED = "DECISION_RECOMMENDED"
    REVIEW_STARTED = "REVIEW_STARTED"
    REVIEW_COMPLETED = "REVIEW_COMPLETED"
    DECISION_MADE = "DECISION_MADE"
    OVERRIDE_CREATED = "OVERRIDE_CREATED"
    OUTCOME_RECEIVED = "OUTCOME_RECEIVED"
    MODEL_CREATED = "MODEL_CREATED"
    MODEL_VALIDATED = "MODEL_VALIDATED"
    MODEL_PROMOTED = "MODEL_PROMOTED"
    MODEL_RETIRED = "MODEL_RETIRED"
    POLICY_CREATED = "POLICY_CREATED"
    POLICY_CHANGED = "POLICY_CHANGED"
    CONFIG_CHANGED = "CONFIG_CHANGED"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACCESS_DENIED = "ACCESS_DENIED"
    CLIENT_CREATED = "CLIENT_CREATED"
    APPLICATION_DATA_INGESTED = "APPLICATION_DATA_INGESTED"
    ELIGIBILITY_CHECKED = "ELIGIBILITY_CHECKED"
    LINEAGE_RECORDED = "LINEAGE_RECORDED"


class AuditService:
    """Orchestre l'enregistrement des evenements d'audit."""

    def __init__(self, db: Session) -> None:
        self._repo = AuditRepository(db)

    def log(
        self,
        event: AuditEventType,
        *,
        institution_id: Optional[uuid.UUID] = None,
        actor_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Enregistre un evenement append-only et retourne l'entite creee."""
        return self._repo.create(
            event=event.value,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            request_id=request_id,
            details_json=details,
        )

    def list(
        self,
        institution_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEvent]:
        return self._repo.list(
            institution_id=institution_id,
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset,
        )
