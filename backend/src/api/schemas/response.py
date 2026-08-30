"""Schemas de reponse de l'API (Pydantic v2).

Reponse normalisee incluant la PD, le niveau de confiance et la
recommandation de decision issue du DecisionEngine.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class DecisionItem(BaseModel):
    """Representation d'une decision (recommandation) en sortie d'API."""

    model_config = ConfigDict(from_attributes=True)

    prediction_id: UUID
    customer_id: int
    pd_score: float
    confidence_level: str
    confidence_score: float
    recommendation: str
    model_version: str
    created_at: datetime


class DecisionListResponse(BaseModel):
    total: int
    items: list[DecisionItem]


class AuditItem(BaseModel):
    """Representation d'une entree du journal d'audit."""

    model_config = ConfigDict(from_attributes=True)

    audit_id: UUID
    prediction_id: UUID | None
    agent_id: str | None
    agent_decision: str | None
    agent_justification: str | None
    is_override: bool
    created_at: datetime


class AuditListResponse(BaseModel):
    total: int
    items: list[AuditItem]


class ModelItem(BaseModel):
    """Representation d'une version de modele."""

    model_config = ConfigDict(from_attributes=True)

    version_id: int
    version_name: str
    mlflow_run_id: str | None
    roc_auc: float | None
    pr_auc: float | None
    brier_score: float | None
    status: str
    deployed_at: datetime | None
    created_at: datetime


class ModelListResponse(BaseModel):
    items: list[ModelItem]
