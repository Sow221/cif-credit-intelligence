"""Gouvernance du data lineage (P0, etape 7).

Garantit la tracabilite de chaque feature utilise pour une decision :

    SOURCE
      v
    RAW FIELD
      v
    TRANSFORMATION
      v
    FEATURE
      v
    MODEL
      v
    PREDICTION
      v
    DECISION

Chaque feature utilise pour une decision doit pouvoir etre relie a sa source
(la table data_lineage consomme : application, source, raw_field, transformation,
feature, model_version, prediction, decision).
"""

import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.core.exceptions import LineageError
from src.db.models import DataLineage
from src.repositories.lineage_repository import LineageRepository


class LineageRecord(BaseModel):
    """Etape de tracabilite (source -> feature) pour une application."""

    model_config = ConfigDict(from_attributes=True)

    raw_field: Optional[str] = None
    transformation: Optional[str] = None
    feature: Optional[str] = None
    model_version: Optional[str] = None
    source_code: Optional[str] = None
    source_type: Optional[str] = None
    prediction_id: Optional[uuid.UUID] = None
    decision_id: Optional[uuid.UUID] = None


class LineageGuard:
    """Verifie qu'une decision repose sur une tracabilite complete."""

    def traceable(self, records: List[DataLineage]) -> bool:
        """Vrai si chaque enregistrement est relie a une source."""
        if not records:
            return False
        for record in records:
            if record.source_id is None:
                return False
        return True


class LineageService:
    """Enregistre et reconstruit la provenance source -> feature."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = LineageRepository(db)
        self._audit = AuditService(db)
        self._guard = LineageGuard()

    def record(
        self,
        *,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        actor_id: Optional[str],
        feature: str,
        raw_field: Optional[str] = None,
        transformation: Optional[str] = None,
        source_id: Optional[uuid.UUID] = None,
        model_version: Optional[str] = None,
        prediction_id: Optional[uuid.UUID] = None,
        request_id: Optional[str] = None,
    ) -> DataLineage:
        """Enregistre la provenance d'un feature pour une application."""
        record = self._repo.create(
            application_id=application_id,
            source_id=source_id,
            raw_field=raw_field,
            transformation=transformation,
            feature=feature,
            model_version=model_version,
            prediction_id=prediction_id,
            decision_id=None,
        )
        self._db.flush()
        self._audit.log(
            AuditEventType.LINEAGE_RECORDED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="application",
            entity_id=str(application_id),
            request_id=request_id,
            details={"feature": feature, "source_id": str(source_id) if source_id else None},
        )
        self._db.commit()
        self._db.refresh(record)
        return record

    def resolve_source(
        self, *, feature: str, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> LineageRecord:
        """Retourne la source d'un feature (relie le feature a sa source)."""
        step = self._repo.resolve_feature(feature, application_id, institution_id)
        if step is None:
            raise LineageError(
                f"Feature {feature} sans provenance enregistree",
                details={"feature": feature},
            )
        source = self._repo.get_source(step.source_id) if step.source_id else None
        return LineageRecord(
            raw_field=step.raw_field,
            transformation=step.transformation,
            feature=step.feature,
            model_version=step.model_version,
            source_code=source.code if source else None,
            source_type=source.type if source else None,
            prediction_id=step.prediction_id,
            decision_id=step.decision_id,
        )

    def lineage_for_application(
        self, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> List[LineageRecord]:
        """Reconstruit la chaine source -> feature pour une application."""
        records = self._repo.list_for_application(application_id, institution_id)
        result: List[LineageRecord] = []
        source_cache: Dict[uuid.UUID, str] = {}
        for step in records:
            src_code = None
            if step.source_id is not None:
                if step.source_id not in source_cache:
                    s = self._repo.get_source(step.source_id)
                    source_cache[step.source_id] = s.code if s else "UNKNOWN"
                src_code = source_cache[step.source_id]
            result.append(
                LineageRecord(
                    raw_field=step.raw_field,
                    transformation=step.transformation,
                    feature=step.feature,
                    model_version=step.model_version,
                    source_code=src_code,
                    prediction_id=step.prediction_id,
                    decision_id=step.decision_id,
                )
            )
        return result

    def assert_traceable(
        self, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> None:
        """Leve LineageError si un feature du perimeter n'a pas de source."""
        records = self._repo.list_for_application(application_id, institution_id)
        if not self._guard.traceable(records):
            raise LineageError(
                "Un feature utilise n'est pas reliee a sa source",
                details={"traced": len(records)},
            )
