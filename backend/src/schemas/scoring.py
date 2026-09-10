from __future__ import annotations

from pydantic import BaseModel


class ScoreResponse(BaseModel):
    prediction_id: str
    pd_raw: float
    pd_calibrated: float | None = None
    model_version: str
    feature_set_id: str
    snapshot_id: str
    calibration_version: str | None = None
