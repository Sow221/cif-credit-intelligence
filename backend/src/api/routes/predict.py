"""Route de prediction de defaut (POST /v1/predict).

Enchainement : schema -> detection thin-file -> features -> PD -> confiance
-> decision -> audit. Un client thin-file ne declenche JAMAIS l'appel au
modele et aboutit systematiquement a REVUE_HUMAINE.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request

from src.api.schemas.request import PredictionRequest
from src.api.schemas.response import (
    ConfidenceScore,
    PredictionResponse,
    Recommendation,
)
from src.config.settings import Settings
from src.models.predictor import ModelUnavailableError, Predictor
from src.services.audit_service import AuditService
from src.services.confidence import ConfidenceService
from src.services.decision_engine import DecisionEngine
from src.services.feature_service import FeatureService, FeatureServiceError

router = APIRouter(tags=["prediction"])

settings = Settings()
audit = AuditService()
decision_engine = DecisionEngine()

try:
    predictor = Predictor(settings.model_path)
except ModelUnavailableError:
    predictor = None


@router.post("/v1/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, req: Request) -> PredictionResponse:
    request_id = req.state.request_id
    payload = request.model_dump()

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
        pd_score = predictor.predict_pd(payload)
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
    return response
