from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies.permissions import require_permission
from src.audit.audit_service import AuditService
from src.core.database import get_db
from src.models.database import User
from src.schemas.audit import AuditEventResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEventResponse])
def list_audit_events(
    event_type: str | None = None,
    entity_type: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("audit:read")),
) -> list[AuditEventResponse]:
    service = AuditService(db)
    events = service.list_events(user.institution_id, event_type, entity_type, limit)
    return [
        AuditEventResponse(
            event_id=str(e.event_id),
            institution_id=str(e.institution_id),
            actor_id=str(e.actor_id) if e.actor_id else None,
            event_type=e.event_type,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            created_at=str(e.created_at),
        )
        for e in events
    ]
