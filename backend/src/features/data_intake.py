from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.core.exceptions import (
    ConsentRequiredError,
    DataTemporalityFailureError,
    SourceUnavailableError,
)
from src.models.database import ApplicationData, Consent, DataSource


class DataIntakeService:
    def __init__(self, db: Session):
        self.db = db

    def validate_and_store(
        self, application_id: uuid.UUID, institution_id: uuid.UUID, records: list[dict[str, Any]]
    ) -> list[ApplicationData]:
        """Validate consent, source, temporality, then store records."""
        stored = []
        for rec in records:
            source = (
                self.db.query(DataSource)
                .filter(DataSource.source_id == rec["source_id"], DataSource.is_active)
                .first()
            )
            if not source:
                raise SourceUnavailableError(str(rec["source_id"]))
            consent = None
            if rec.get("consent_id"):
                consent = (
                    self.db.query(Consent)
                    .filter(Consent.consent_id == rec["consent_id"], Consent.status == "GRANTED")
                    .first()
                )
                if not consent:
                    raise ConsentRequiredError(str(rec["source_id"]))
            # Temporal guard: observed_at must not be in the future relative to now
            if rec["observed_at"] > datetime.now(UTC):
                raise DataTemporalityFailureError("DonnÃ©es observÃ©es dans le futur")
            data = ApplicationData(
                application_id=application_id,
                source_id=rec["source_id"],
                consent_id=rec.get("consent_id"),
                field_name=rec["field_name"],
                field_value=rec["field_value"],
                data_type=rec["data_type"],
                observed_at=rec["observed_at"],
                quality_status="PENDING",
                availability_status="AVAILABLE",
            )
            self.db.add(data)
            stored.append(data)
        self.db.commit()
        for d in stored:
            self.db.refresh(d)
        return stored
