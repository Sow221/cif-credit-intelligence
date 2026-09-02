"""Schemas Pydantic de la revue humaine (P0, etape 16)."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    application_id: uuid.UUID
    review_reason: str = Field(..., min_length=1, max_length=200)


class ReviewAssign(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assigned_to: str = Field(..., min_length=1, max_length=100)


class ReviewComplete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    final_action: str = Field(..., pattern="^(APPROVE|DECLINE|REQUEST_INFORMATION)$")


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: uuid.UUID
    application_id: uuid.UUID
    assigned_to: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    review_reason: Optional[str] = None
    final_action: Optional[str] = None