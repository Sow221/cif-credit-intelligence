from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.core.exceptions import ModelNotApprovedError, ModelNotAvailableError
from src.models.calibration import CalibrationService
from src.models.database import ModelVersion, Prediction
from src.models.risk_engine import RiskEngine
from src.models.uncertainty import UncertaintyService


class ScoringService:
    def __init__(self, db: Session):
        self.db = db
        self.risk_engine = RiskEngine()
        self.calibration = CalibrationService()
        self.uncertainty = UncertaintyService()

    def score(
        self, application_id: uuid.UUID, snapshot_id: uuid.UUID, features: dict[str, Any]
    ) -> dict[str, Any]:
        model = self.db.query(ModelVersion).filter(ModelVersion.status == "PRODUCTION").first()
        if not model:
            raise ModelNotAvailableError()
        if model.status != "PRODUCTION":
            raise ModelNotApprovedError(model.version)
        pd_raw = self.risk_engine.score(features, model)
        pd_calibrated = self.calibration.calibrate(pd_raw, model.model_version_id)
        prediction = Prediction(
            application_id=application_id,
            model_version_id=model.model_version_id,
            snapshot_id=snapshot_id,
            pd_raw=pd_raw,
            pd_calibrated=pd_calibrated,
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        uncertainty = self.uncertainty.assess(pd_raw, features)
        return {
            "prediction_id": str(prediction.prediction_id),
            "pd_raw": pd_raw,
            "pd_calibrated": pd_calibrated,
            "model_version": model.version,
            "snapshot_id": str(snapshot_id),
            "uncertainty": uncertainty,
        }
