from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies.permissions import require_permission
from src.audit.audit_service import AuditService
from src.core.database import get_db
from src.features.feature_engine import FeatureEngineService
from src.models.database import User
from src.schemas.scoring import ScoreResponse
from src.services.scoring_service import ScoringService

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/{application_id}/score", response_model=ScoreResponse)
def score_application(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("applications:write")),
) -> ScoreResponse:
    feature_engine = FeatureEngineService()
    features = feature_engine.build_features({}, "FULL_ADMISSIBLE")
    snapshot_hash = feature_engine.compute_snapshot_hash(features)
    scoring = ScoringService(db)
    result = scoring.score(application_id, uuid.uuid4(), features)
    AuditService(db).record(
        user.institution_id, "SCORE_CREATED", "prediction", result["prediction_id"], user.user_id
    )
    return ScoreResponse(**result)
