"""Route de consultation du journal d'audit.

Endpoints :
- GET /v1/audit -> entrees d'audit (journalisees, paginees)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from src.api.middleware.rate_limit import get_limit, limiter
from src.api.schemas.response import AuditItem, AuditListResponse
from src.db.models import AuditLog
from src.db.session import get_db

router = APIRouter(tags=["audit"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/v1/audit", response_model=AuditListResponse)
@limiter.limit(get_limit("rate_audit"))
async def get_audit_log(
    request: Request,
    db: DbSession,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> AuditListResponse:
    """Retourne les entrees d'audit les plus recentes."""
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return AuditListResponse(
        total=len(logs), items=[AuditItem.model_validate(log) for log in logs]
    )