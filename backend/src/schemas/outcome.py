"""Schemas Pydantic du loan outcome (P0, etape 18 / 36)."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class OutcomeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    application_id: uuid.UUID
    loan_id: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=30)
    outcome_date: Optional[datetime] = None
    days_past_due: Optional[int] = Field(None, ge=0)
    default_status: Optional[bool] = None
    recovery_amount: Optional[float] = Field(None, ge=0)
    source: Optional[str] = Field(None, max_length=50)


class OutcomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    outcome_id: uuid.UUID
    application_id: uuid.UUID
    loan_id: Optional[str] = None
    status: Optional[str] = None
    outcome_date: Optional[datetime] = None
    days_past_due: Optional[int] = None
    default_status: Optional[bool] = None
    recovery_amount: Optional[float] = None
    source: Optional[str] = None
    created_at: datetime