"""Schemas Pydantic du consentement (P0, etape 6)."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.governance.consent import ConsentStatus


class ConsentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_id: uuid.UUID
    status: ConsentStatus
    purpose: str = Field(..., min_length=1, max_length=200)
    source_id: Optional[uuid.UUID] = None
    version: str = "1"


class ConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    consent_id: uuid.UUID
    client_id: uuid.UUID
    institution_id: uuid.UUID
    source_id: Optional[uuid.UUID] = None
    purpose: str
    status: str
    version: str
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime


class ConsentCheckResponse(BaseModel):
    allowed: bool
    status: str
    reason: str
