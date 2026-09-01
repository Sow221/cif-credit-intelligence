"""Route de prediction de defaut (POST /v1/predict).

Enchainement : schema -> detection thin-file -> features -> PD -> confiance
-> decision -> audit -> persistance des decisions dans la base
(consommee par /v1/decisions et /v1/audit).
"""

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.routes.metrics import inc_prediction, set_model_loaded
from src.api.schemas.request import PredictionRequest
from src.api.schemas.response import (
    ConfidenceScore,
    PredictionResponse,
    Recommendation,
)
from src.config.settings import Settings
from src.db.models import Customer, Prediction
from src.db.session import get_db
from src.models.predictor import ModelUnavailableError, Predictor
from src.models.risk_engine import RiskEngine
from src.services.audit_service import AuditService
from src.services.confidence import ConfidenceService
from src.services.decision_engine import DecisionEngine
from src.services.feature_service import FeatureService, FeatureServiceError

router = APIRouter(tags=["prediction"])

DbSession = Annotated[Session, Depends(get_db)]

settings = Settings()
audit = AuditService()
decision_engine = DecisionEngine()

try:
    predictor = Predictor(
        model_path=settings.model_path,
        model_uri=settings.model_uri,
        mlflow_tracking_uri=settings.mlflow_tracking_uri,
    )
    set_model_loaded(True)
except ModelUnavailableError:
    predictor = None
    set_model_loaded(False)

# Le scoring passe par le RiskEngine (jamais XGBClassifier/MLflow en direct).
risk_engine = RiskEngine(predictor)


def _persist_prediction(
    db: Session,
    customer_id: int,
    age: int,
    seniority_months: int,
    pd_score: float,
    confidence_level: str,
    confidence_score: float,
    recommendation: str,
    model_version: str,
    features_used: dict,
    request_id: str,
) -> None:
    """Upsert du client puis insertion de la prediction en base."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        customer = Customer(
            customer_id=customer_id,
            age=age,
            seniority_months=seniority_months,
        )
        db.add(customer)
    else:
        customer.age = age
        customer.seniority_months = seniority_months

    prediction = Prediction(
        customer_id=customer_id,
        pd_score=pd_score,
        confidence_level=confidence_level,
        confidence_score=confidence_score,
        recommendation=recommendation,
        model_version=model_version,
        features_used=features_used or None,
        request_id=uuid.UUID(request_id) if _is_uuid(request_id) else None,
    )
    db.add(prediction)
    db.commit()


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


@router.post("/v1/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest, req: Request, db: DbSession
) -> PredictionResponse:
    request_id = req.state.request_id
    payload = request.model_dump()
    inc_prediction()

    # Cas Thin-File : pas d'appel au modele, decision = REVUE_HUMAINE
    if FeatureService.is_thin_file(payload) or request.has_history is False:
        response = PredictionResponse(
            pd_score=None,
            confidence=ConfidenceScore(level="FAIBLE", score=0.35),
            recommendation=Recommendation(
                decision="REVUE_HUMAINE",
                raison="Client Thin-File - information insuffisante",
            ),
            is_thin_file=True,
            model_version=None,
            request_id=request_id,
            timestamp=datetime.now(UTC).isoformat(),
        )
        audit.log_prediction(
            request_id=request_id,
            customer_id=request.customer_id,
            pd_score=None,
            decision="REVUE_HUMAINE",
            confidence_level="FAIBLE",
            is_thin_file=True,
        )
        return response

    if predictor is None:
        raise HTTPException(status_code=503, detail="Modele indisponible")

    try:
        risk_result = risk_engine.score_payload(payload, feature_set="FULL_ADMISSIBLE")
        pd_score = risk_result.pd_raw
    except FeatureServiceError as exc:
        # Donnees incompletes -> 422 (jamais de zeros artificiels)
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    confidence = ConfidenceService.compute(
        request.n_past_loans, request.seniority_months, True
    )
    recommendation = DecisionEngine().evaluate(
        pd_score, confidence["level"], False, request.n_past_loans
    )

    response = PredictionResponse(
        pd_score=pd_score,
        confidence=ConfidenceScore(level=confidence["level"], score=confidence["score"]),
        recommendation=Recommendation(**recommendation),
        is_thin_file=False,
        model_version=predictor.model_version,
        request_id=request_id,
        timestamp=datetime.now(UTC).isoformat(),
    )
    audit.log_prediction(
        request_id=request_id,
        customer_id=request.customer_id,
        pd_score=pd_score,
        decision=response.recommendation.decision,
        confidence_level=confidence["level"],
        is_thin_file=False,
        model_version=predictor.model_version,
    )

    # Persistance pour /v1/decisions, /v1/audit et la tracabilite reglementaire.
    features_used = predictor.feature_vector(payload)
    _persist_prediction(
        db=db,
        customer_id=request.customer_id,
        age=request.age,
        seniority_months=request.seniority_months,
        pd_score=pd_score,
        confidence_level=confidence["level"],
        confidence_score=confidence["score"],
        recommendation=response.recommendation.decision,
        model_version=predictor.model_version,
        features_used=features_used,
        request_id=request_id,
    )
    return response
