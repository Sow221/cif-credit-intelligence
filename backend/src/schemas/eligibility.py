"""Schemas de l'eligibilite (P0, etape 4).

L'eligibilite est DISTINCTE du risque et de la decision. Le systeme repond
d'abord ELIGIBLE ?, puis WHAT IS THE RISK ?, puis WHAT IS THE DECISION ?.

Les regles d'eligibilite sont CONFIGURABLES et versionnees (aucun seuil en dur
dans la logique metier) : le service accepte des regles injectees (dont la
source a terme est decision_policies.eligibility_rules).
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    REVIEW = "REVIEW"


class EligibilityRules(BaseModel):
    """Regles d'eligibilite configurables et versionnees."""

    model_config = ConfigDict(extra="forbid")

    rules_version: str = "1.0"
    age_min: Optional[int] = Field(None, ge=0)
    age_max: Optional[int] = Field(None, gt=0)
    amount_min: Optional[float] = Field(None, ge=0)
    amount_max: Optional[float] = Field(None, ge=0)
    term_min: Optional[int] = Field(None, ge=1)
    term_max: Optional[int] = Field(None, ge=1)
    allowed_currencies: Optional[List[str]] = None
    allowed_products: Optional[List[str]] = None


class EligibilityInput(BaseModel):
    """Donnees necessaires a la verification d'eligibilite."""

    model_config = ConfigDict(extra="forbid")

    client_age: Optional[float] = None
    requested_amount: Optional[float] = None
    currency: Optional[str] = None
    requested_term: Optional[int] = None
    product_id: Optional[str] = None


class EligibilityReason(BaseModel):
    code: str
    message: str


class EligibilityResult(BaseModel):
    """Resultat de la verification d'eligibilite."""

    status: EligibilityStatus
    eligible: bool
    reasons: List[EligibilityReason] = Field(default_factory=list)
    rules_version: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
