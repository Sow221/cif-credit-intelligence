from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    application_id: uuid.UUID


class DecisionResponse(BaseModel):
    decision_id: str
    application_id: str
    recommendation: str
    final_decision: str | None = None
    proposed_amount: float | None = None
    proposed_term: int | None = None
    decision_reason: str | None = None
    policy_version: int | None = None


class OverrideRequest(BaseModel):
    final_decision: str = Field(..., pattern=r"^(APPROVE|DECLINE)$")
    override_reason: str = Field(..., min_length=1)


class OverrideResponse(BaseModel):
    override_id: str
    decision_id: str
    original_recommendation: str
    final_decision: str
    override_reason: str
    actor_id: str
    created_at: str
