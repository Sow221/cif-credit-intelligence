from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationBase(BaseModel):
    client_id: uuid.UUID
    product_id: str = Field(..., max_length=50)
    requested_amount: float = Field(..., gt=0)
    currency: str = Field(default="XOF", max_length=3)
    requested_term: int = Field(..., gt=0)
    purpose: str | None = None


class CreateApplicationRequest(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    application_id: uuid.UUID
    institution_id: uuid.UUID
    status: str
    application_timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
