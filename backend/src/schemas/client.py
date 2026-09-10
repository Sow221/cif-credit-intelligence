from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ClientBase(BaseModel):
    first_name: str = Field(..., max_length=255)
    last_name: str = Field(..., max_length=255)
    date_of_birth: datetime | None = None
    phone: str | None = None
    email: str | None = None
    zone: str | None = None
    sector: str | None = None
    external_ref: str | None = None


class CreateClientRequest(ClientBase):
    pass


class ClientResponse(ClientBase):
    client_id: uuid.UUID
    institution_id: uuid.UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
