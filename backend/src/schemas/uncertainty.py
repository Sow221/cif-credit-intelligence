from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class UncertaintyResponse(BaseModel):
    uncertainty_id: str
    prediction_id: str
    method: str
    version: str
    score: float
    level: str
    factors: list[dict[str, Any]] = []
