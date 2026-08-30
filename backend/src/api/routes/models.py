"""Route de consultation des versions de modele.

Endpoints :
- GET /v1/models -> versions de modele enregistrees (MLflow)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.api.middleware.rate_limit import get_limit, limiter
from src.api.schemas.response import ModelItem, ModelListResponse
from src.db.models import ModelVersion
from src.db.session import get_db

router = APIRouter(tags=["models"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/v1/models", response_model=ModelListResponse)
@limiter.limit(get_limit("rate_models"))
async def get_models(request: Request, db: DbSession) -> ModelListResponse:
    """Liste les versions de modele, de la plus recente a la plus ancienne."""
    models = (
        db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()
    )
    return ModelListResponse(items=[ModelItem.model_validate(m) for m in models])