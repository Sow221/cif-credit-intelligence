"""Schemas Pydantic du client (P0, etape 1).

Le client_id interne est distinct des identifiants externes.
L'institution provient du contexte authentifie (multi-tenancy), jamais du
corps de requete : le tenant est injecte cote service/route.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ClientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_ref: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, max_length=20)
    status: str = Field("ACTIVE", max_length=20)


class ClientUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_ref: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    client_id: uuid.UUID
    institution_id: uuid.UUID
    external_ref: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
