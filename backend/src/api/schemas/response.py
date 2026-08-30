"""Schemas de reponse de l'API (Pydantic v2).

Reponse normalisee incluant la PD, le niveau de confiance et la
recommandation de decision issue du DecisionEngine.
"""


from pydantic import BaseModel, Field


class ConfidenceScore(BaseModel):
    level: str = Field(..., pattern="^(FAIBLE|MOYENNE|ELEVEE)$")
    score: float = Field(..., ge=0, le=1)


class Recommendation(BaseModel):
    decision: str = Field(..., pattern="^(APPROBATION|REVUE_HUMAINE|AJUSTEMENT|REFUS)$")
    raison: str


class PredictionResponse(BaseModel):
    status: str = "success"
    pd_score: float | None = Field(None, ge=0, le=1)
    confidence: ConfidenceScore
    recommendation: Recommendation
    is_thin_file: bool = False
    model_version: str | None = None
    request_id: str
    timestamp: str
