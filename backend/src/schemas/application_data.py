from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationDataBase(BaseModel):
    source_id: uuid.UUID
    field_name: str = Field(..., max_length=255)
    field_value: str
    data_type: str = Field(..., max_length=50)
    observed_at: datetime
    consent_id: uuid.UUID | None = None


class SubmitDataRequest(BaseModel):
    records: list[ApplicationDataBase]


class ApplicationDataResponse(ApplicationDataBase):
    data_id: uuid.UUID
    application_id: uuid.UUID
    quality_status: str
    availability_status: str
    received_at: datetime

    model_config = {"from_attributes": True}
