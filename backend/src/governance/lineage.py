from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from src.models.database import DataLineage


class LineageService:
    def __init__(self, db: Session):
        self.db = db

    def trace(self, application_id: uuid.UUID) -> list[DataLineage]:
        return self.db.query(DataLineage).filter(DataLineage.application_id == application_id).all()

    def record(
        self,
        application_id: uuid.UUID,
        source_id: uuid.UUID,
        field_name: str,
        feature_name: str | None = None,
        prediction_id: uuid.UUID | None = None,
        decision_id: uuid.UUID | None = None,
    ) -> DataLineage:
        lineage = DataLineage(
            application_id=application_id,
            source_id=source_id,
            field_name=field_name,
            feature_name=feature_name,
            prediction_id=prediction_id,
            decision_id=decision_id,
        )
        self.db.add(lineage)
        self.db.commit()
        self.db.refresh(lineage)
        return lineage

    def is_traceable(self, feature_name: str, application_id: uuid.UUID) -> bool:
        return (
            self.db.query(DataLineage)
            .filter(
                DataLineage.application_id == application_id,
                DataLineage.feature_name == feature_name,
            )
            .first()
            is not None
        )
