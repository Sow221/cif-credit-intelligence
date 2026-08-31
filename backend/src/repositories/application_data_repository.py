"""Repository des donnees de candidature (P0, etape 3).

Le scope institution est applique par jointure avec la table `applications`
(la table application_data ne porte pas de colonne institution). Toute lecture
verifie l'appartenance de l'application au tenant demande (multi-tenancy).
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Application, ApplicationData, DataSource


class ApplicationDataRepository:
    """Acces persistant aux donnees de candidature (scope tenant)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        application_id: uuid.UUID,
        source_id: Optional[uuid.UUID],
        field_name: str,
        field_value: dict | None,
        data_type: Optional[str],
        observed_at: Optional[datetime],
        received_at: datetime,
        consent_id: Optional[uuid.UUID],
        quality_status: str,
        availability_status: str,
    ) -> ApplicationData:
        entry = ApplicationData(
            application_id=application_id,
            source_id=source_id,
            field_name=field_name,
            field_value=field_value,
            data_type=data_type,
            observed_at=observed_at,
            received_at=received_at,
            consent_id=consent_id,
            quality_status=quality_status,
            availability_status=availability_status,
        )
        self._db.add(entry)
        return entry

    def list_for_application(
        self, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> List[ApplicationData]:
        """Liste les donnees de l'application, verifiant le scope tenant."""
        stmt = (
            select(ApplicationData)
            .join(Application, Application.application_id == ApplicationData.application_id)
            .where(
                ApplicationData.application_id == application_id,
                Application.institution_id == institution_id,
            )
            .order_by(ApplicationData.field_name)
        )
        return list(self._db.scalars(stmt).all())

    def list_active_sources(self) -> List[DataSource]:
        """Liste les sources de donnees actives (registre systeme)."""
        stmt = select(DataSource).where(DataSource.active.is_(True)).order_by(DataSource.code)
        return list(self._db.scalars(stmt).all())

    def get_source_by_code(self, code: str) -> Optional[DataSource]:
        stmt = select(DataSource).where(DataSource.code == code)
        return self._db.scalar(stmt)

    def update_quality_status(
        self, entry: ApplicationData, quality_status: str, availability_status: str
    ) -> None:
        entry.quality_status = quality_status
        entry.availability_status = availability_status
