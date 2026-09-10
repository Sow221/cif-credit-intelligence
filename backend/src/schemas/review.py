from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class ReviewResponse(BaseModel):
    review_id: str
    application_id: str
    assigned_to: str | None = None
    status: str
    review_reason: str
    final_action: str | None = None
    started_at: str | None = None
    completed_at: str | None = None


class AssignReviewRequest(BaseModel):
    assigned_to: uuid.UUID


class CompleteReviewRequest(BaseModel):
    final_action: str = Field(..., pattern=r"^(APPROVE|DECLINE)$")
