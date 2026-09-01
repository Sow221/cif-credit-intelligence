"""Repository du data lineage (P0, etape 7).

La table data_lineage ne porte pas de colonne institution : le scope tenant est
applique par jointure avec la table `applications` (multi-tenancy), comme pour
application_data.
"""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Application, DataLineage, DataSource


class LineageRepository:
    """Acces persistant a la tracabilite source -> field -> feature."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        application_id: uuid.UUID,
        source_id: Optional[uuid.UUID],
        raw_field: Optional[str],
        transformation: Optional[str],
        feature: Optional[str],
        model_version: Optional[str],
        prediction_id: Optional[uuid.UUID],
        decision_id: Optional[uuid.UUID],
    ) -> DataLineage:
        record = DataLineage(
            application_id=application_id,
            source_id=source_id,
            raw_field=raw_field,
            transformation=transformation,
            feature=feature,
            model_version=model_version,
            prediction_id=prediction_id,
            decision_id=decision_id,
        )
        self._db.add(record)
        return record

    def list_for_application(
        self, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> List[DataLineage]:
        """Liste les etapes de lineage d'une application (scope tenant)."""
        stmt = (
            select(DataLineage)
            .join(Application, Application.application_id == DataLineage.application_id)
            .where(
                DataLineage.application_id == application_id,
                Application.institution_id == institution_id,
            )
            .order_by(DataLineage.created_at.asc())
        )
        return list(self._db.scalars(stmt).all())

    def resolve_feature(
        self, feature: str, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> Optional[DataLineage]:
        """Retourne l'etape de lineage produisant le feature demande."""
        stmt = (
            select(DataLineage)
            .join(Application, Application.application_id == DataLineage.application_id)
            .where(
                DataLineage.application_id == application_id,
                DataLineage.feature == feature,
                Application.institution_id == institution_id,
            )
            .order_by(DataLineage.created_at.asc())
        )
        return self._db.scalar(stmt)

    def get_source(self, source_id: uuid.UUID) -> Optional[DataSource]:
        stmt = select(DataSource).where(DataSource.source_id == source_id)
        return self._db.scalar(stmt)
