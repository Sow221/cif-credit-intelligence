from __future__ import annotations

import math
import uuid


class CalibrationService:
    def calibrate(self, pd_raw: float, model_version_id: uuid.UUID | None = None) -> float:
        """Apply Platt scaling calibration."""
        clipped = max(0.0001, min(0.9999, pd_raw))
        logit = math.log(clipped / (1 - clipped))
        calibrated_logit = logit * 0.8 + 0.1
        calibrated = 1 / (1 + math.exp(-calibrated_logit))
        return round(max(0.001, min(0.999, calibrated)), 6)
