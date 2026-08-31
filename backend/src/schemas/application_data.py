"""Schemas Pydantic des donnees de candidature (P0, etape 3).

Representent la matiere premiere brute (raw data) d'une application, avant
profilage et scoring. L'institution provient du contexte authentifie
(multi-tenancy) et n'est jamais portee par le corps de requete.
"""

import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApplicationDataEntry(BaseModel):
    """Une donnee brute de candidature : nom de champ + valeur + metadata.

    La source est referencee par `source_code` (stable) ou `source_id`.
    Le champ `field_value` est une valeur JSON quelconque.
    """

    model_config = ConfigDict(extra="forbid")

    field_name: str = Field(..., min_length=1, max_length=200)
    field_value: Optional[Any] = None
    data_type: Optional[str] = Field(None, max_length=50)
    source_code: Optional[str] = Field(None, max_length=50)
    source_id: Optional[uuid.UUID] = None
    observed_at: Optional[datetime] = None
    consent_id: Optional[uuid.UUID] = None


class ApplicationDataIngest(BaseModel):
    """Lot de donnees brutes a enregistrer pour une application."""

    model_config = ConfigDict(extra="forbid")

    entries: List[ApplicationDataEntry] = Field(..., min_length=1)


class ApplicationDataEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entry_id: uuid.UUID
    application_id: uuid.UUID
    source_id: Optional[uuid.UUID] = None
    field_name: str
    field_value: Optional[Any] = None
    data_type: Optional[str] = None
    observed_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    consent_id: Optional[uuid.UUID] = None
    quality_status: Optional[str] = None
    availability_status: Optional[str] = None


class DataIngestSummary(BaseModel):
    """Resume de l'ingestion : nombre de champs enregistres et sources vues."""

    ingested: int
    sources: List[str]
    quality_status: str
