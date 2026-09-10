from __future__ import annotations

from pydantic import BaseModel


class InformationProfileResponse(BaseModel):
    profile_id: str
    application_id: str
    applicant_status: str
    credit_depth: str
    financial_depth: str
    business_depth: str
    relationship_depth: str
    data_quality: str
    information_state: str
    profile_version: int
    config_version: int
