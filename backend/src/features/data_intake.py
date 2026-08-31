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
from src.features.data_quality import (
    DataQualityChecker,
    DataQualityConfig,
    DataQualityField,
    DataQualityResult,
    DataQualityStatus,
    DataSourceStatus,
)
from src.governance.consent import ConsentGuard, ConsentStatus
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

    def validate(
        self,
        *,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> DataQualityResult:
        """Valide la qualite des donnees ingerees (etapes 5 et 8).

        Construit les champs a partir des entrees, applique le DataQualityChecker
        (6 controles) + le guard temporal d'octroi, met a jour quality_status et
        journalise l'audit DATA_VALIDATED.
        """
        application = self._apps.get(application_id, institution_id)
        if application is None:
            raise NotFoundError(f"Application {application_id} introuvable")

        entries = self._repo.list_for_application(application_id, institution_id)
        sources = {
            str(s.source_id): s for s in self._repo.list_active_sources()
        }
        guard = ConsentGuard(self._db)
        consent_blocked: list[str] = []

        fields: list[DataQualityField] = []
        for entry in entries:
            source = sources.get(str(entry.source_id)) if entry.source_id else None
            # Guard CONSENT (etape 6) : toute donnee dont le consentement
            # obligatoire n'est pas valide est inutilisable.
            if entry.source_id is not None:
                check = guard.check(
                    client_id=application.client_id,
                    institution_id=institution_id,
                    source_id=entry.source_id,
                )
                if not check.allowed:
                    self._repo.update_quality_status(
                        entry,
                        quality_status="PENDING",
                        availability_status="CONSENT_BLOCKED",
                    )
                    consent_blocked.append(entry.field_name)
                    continue
            fields.append(
                DataQualityField(
                    field_name=entry.field_name,
                    field_value=entry.field_value,
                    data_type=entry.data_type,
                    observed_at=entry.observed_at,
                    source=DataSourceStatus(
                        code=source.code if source else "UNKNOWN",
                        active=bool(source),
                        reliable=True,
                    ),
                )
            )

        config = DataQualityConfig(
            application_timestamp=application.application_timestamp,
        )
        result = DataQualityChecker(config).evaluate(fields)
        result.consent_blocked = consent_blocked
        # Consentement invalide => donnees inutilisables => pas de scoring auto
        # (scenario CONSENT FAILURE : DATA NOT USED, NO AUTOMATIC DECISION).
        if consent_blocked:
            result.checks["consent"] = DataQualityStatus.FAIL
            result.data_ready_for_auto_scoring = False

        # Met a jour le quality_status de chaque entree du perimeter.
        by_name = {e.field_name: e for e in entries}
        for field in fields:
            entry = by_name.get(field.field_name)
            if entry is not None:
                field_issues = [
                    i for i in result.issues if i.field == field.field_name
                ]
                critical = any(i.severity.value == "CRITICAL" for i in field_issues)
                status = "FAIL" if critical else ("WARNING" if field_issues else "PASS")
                self._repo.update_quality_status(
                    entry, quality_status=status, availability_status="AVAILABLE"
                )

        self._db.flush()
        self._audit.log(
            AuditEventType.DATA_VALIDATED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="application",
            entity_id=str(application_id),
            request_id=request_id,
            details={
                "status": result.status.value,
                "checks": {k: v.value for k, v in result.checks.items()},
                "rejected_fields": result.rejected_fields,
                "consent_blocked": consent_blocked,
            },
        )
        self._db.commit()
        return result
