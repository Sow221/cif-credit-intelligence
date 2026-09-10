from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.models.database import Consent


class ConsentService:
    VALID_STATUSES = {"GRANTED", "REFUSED", "REVOKED", "NOT_REQUIRED", "UNKNOWN"}

    def __init__(self, db: Session):
        self.db = db

    def check_consent(self, application_id: uuid.UUID, source_id: uuid.UUID) -> Consent | None:
        return (
            self.db.query(Consent)
            .filter(
                Consent.application_id == application_id,
                Consent.source_id == source_id,
                Consent.status == "GRANTED",
            )
            .first()
        )

    def create(
        self,
        application_id: uuid.UUID,
        client_id: uuid.UUID,
        institution_id: uuid.UUID,
        source_id: uuid.UUID,
        purpose: str,
        status: str = "GRANTED",
    ) -> Consent:
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Statut invalide: {status}")
        consent = Consent(
            application_id=application_id,
            client_id=client_id,
            institution_id=institution_id,
            source_id=source_id,
            purpose=purpose,
            status=status,
            granted_at=datetime.now(UTC) if status == "GRANTED" else None,
        )
        self.db.add(consent)
        self.db.commit()
        self.db.refresh(consent)
        return consent

    def revoke(self, consent_id: uuid.UUID) -> Consent | None:
        consent = self.db.query(Consent).filter(Consent.consent_id == consent_id).first()
        if consent:
            consent.status = "REVOKED"
            consent.revoked_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(consent)
        return consent
