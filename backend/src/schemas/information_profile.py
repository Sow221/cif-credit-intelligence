"""Schemas Pydantic de l'information profiler (P0, etape 8).

Represente le profil d'information d'une candidature : profondeur par
dimension (credit, financial, business, relationship), qualite des donnees,
etat d'information et statut demandeur. L'institution provient du contexte
authentifie (multi-tenancy) et n'est jamais portee par le corps de requete.
"""

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InformationProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: uuid.UUID
    application_id: uuid.UUID
    applicant_status: Optional[str] = None
    credit_depth: str
    financial_depth: str
    business_depth: str
    relationship_depth: str
    data_quality: str
    information_state: str
    profile_version: str
