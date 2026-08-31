"""Schemas Pydantic de l'application de credit (P0, etape 2).

Le lifecycle (status) est distinct de la decision metier :
    DRAFT, SUBMITTED, DATA_VALIDATION, PROFILED, SCORED, REVIEW, DECIDED,
    CANCELLED, DISBURSED, ACTIVE, COMPLETED, DEFAULT
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ApplicationStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    DATA_VALIDATION = "DATA_VALIDATION"
    PROFILED = "PROFILED"
    SCORED = "SCORED"
    REVIEW = "REVIEW"
    DECIDED = "DECIDED"
    CANCELLED = "CANCELLED"
    DISBURSED = "DISBURSED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    DEFAULT = "DEFAULT"


class ApplicationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_id: uuid.UUID
    product_id: str = Field(..., max_length=50)
    requested_amount: float = Field(..., gt=0)
    currency: str = Field("XOF", max_length=10)
    requested_term: Optional[int] = Field(None, ge=1)
    purpose: Optional[str] = Field(None, max_length=200)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: uuid.UUID
    institution_id: uuid.UUID
    client_id: uuid.UUID
    product_id: str
    requested_amount: float
    currency: str
    requested_term: Optional[int] = None
    purpose: Optional[str] = None
    status: str
    application_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
