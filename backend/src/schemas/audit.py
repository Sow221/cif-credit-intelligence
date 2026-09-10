from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    event_id: str
    institution_id: str
    actor_id: str | None = None
    event_type: str
    entity_type: str | None = None
    entity_id: str | None = None
    details: dict[str, Any] | None = None
    created_at: str
