"""Routes API des feature snapshots (P0, etape 10).

Cree et expose le snapshot immuable d'une candidature. Chaque prediction
consommera ce snapshot ; un ancien snapshot n'est jamais recalcule avec le
code actuel (consigne section 17).
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.dependencies import CurrentUser, require_permission
from src.core.security import Permission
from src.db.session import get_db
from src.features.feature_snapshot import FeatureSnapshotResult, FeatureSnapshotService

router = APIRouter(prefix="/v1/applications", tags=["feature-snapshots"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/{application_id}/snapshot", response_model=FeatureSnapshotResult)
def build_snapshot(
    application_id: uuid.UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> FeatureSnapshotResult:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = FeatureSnapshotService(db)
    return service.build_snapshot(
        application_id=application_id,
        institution_id=uuid.UUID(current_user.institution_id),
        actor_id=current_user.subject,
        request_id=getattr(request.state, "request_id", None),
    )


@router.get("/{application_id}/snapshot/latest", response_model=FeatureSnapshotResult)
def get_latest_snapshot(
    application_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser = Depends(require_permission(Permission.APPLICATION_READ)),
) -> FeatureSnapshotResult:
    if not current_user.institution_id:
        raise HTTPException(status_code=401, detail="Utilisateur sans institution")
    service = FeatureSnapshotService(db)
    snapshot = service.get_latest(
        application_id=application_id,
        institution_id=uuid.UUID(current_user.institution_id),
    )
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Snapshot introuvable")
    return snapshot