"""Ingestion des donnees de candidature (P0, etape 3).

Orchestre l'enregistrement des donnees brutes (raw data) d'une application :
resolution des sources, enregistrement des entrees `application_data`,
journalisation d'audit et commit atomique. L'institution provient du contexte
authentifie (multi-tenancy) ; le scope est verifie cote backend.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.core.exceptions import NotFoundError, SourceUnavailableError
from src.repositories.application_data_repository import ApplicationDataRepository
from src.repositories.application_repository import ApplicationRepository
from src.schemas.application_data import (
    ApplicationDataIngest,
    ApplicationDataEntryResponse,
    DataIngestSummary,
)


class DataIntakeService:
    """Ingestion et stockage des donnees brutes de candidature."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ApplicationDataRepository(db)
        self._apps = ApplicationRepository(db)
        self._audit = AuditService(db)

    def ingest(
        self,
        *,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        payload: ApplicationDataIngest,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> DataIngestSummary:
        # L'application doit exister et appartenir au tenant (multi-tenancy).
        application = self._apps.get(application_id, institution_id)
        if application is None:
            raise NotFoundError(f"Application {application_id} introuvable")

        sources = self._repo.list_active_sources()
        by_code = {s.code: s for s in sources}
        by_id = {str(s.source_id): s for s in sources}

        ingested = 0
        source_codes: set = set()
        now = datetime.now(timezone.utc)

        for entry in payload.entries:
            source = None
            if entry.source_id is not None:
                source = by_id.get(str(entry.source_id))
            elif entry.source_code is not None:
                source = by_code.get(entry.source_code)
                if source is None:
                    raise SourceUnavailableError(
                        f"Source inconnue ou inactive : {entry.source_code}",
                        details={"source_code": entry.source_code},
                    )

            self._repo.create(
                application_id=application_id,
                source_id=source.source_id if source else None,
                field_name=entry.field_name,
                field_value=entry.field_value,
                data_type=entry.data_type,
                observed_at=entry.observed_at,
                received_at=now,
                consent_id=entry.consent_id,
                quality_status="PENDING",
                availability_status="AVAILABLE",
            )
            ingested += 1
            if source is not None:
                source_codes.add(source.code)

        self._db.flush()
        self._audit.log(
            AuditEventType.APPLICATION_DATA_INGESTED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="application",
            entity_id=str(application_id),
            request_id=request_id,
            details={
                "ingested": ingested,
                "sources": sorted(source_codes),
            },
        )
        self._db.commit()
        return DataIngestSummary(
            ingested=ingested,
            sources=sorted(source_codes),
            quality_status="PENDING",
        )

    def list_for_application(
        self,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> list[ApplicationDataEntryResponse]:
        """Liste les donnees brutes d'une application (scope tenant)."""
        application = self._apps.get(application_id, institution_id)
        if application is None:
            raise NotFoundError(f"Application {application_id} introuvable")
        entries = self._repo.list_for_application(application_id, institution_id)
        return [ApplicationDataEntryResponse.model_validate(e) for e in entries]
