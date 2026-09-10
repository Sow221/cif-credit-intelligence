from __future__ import annotations

from pydantic import BaseModel


class EligibilityResult(BaseModel):
    eligible: bool
    reasons: list[str]
    policy_version: str | None = None
