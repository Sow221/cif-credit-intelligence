"""Repository des feature snapshots (P0, etape 10).

La table feature_snapshots ne porte pas de colonne institution : le scope
tenant est applique par jointure avec la table `applications` (multi-tenancy),
comme pour application_data et data_lineage.

Un snapshot est IMMUABLE : on ne modifie jamais un enregistrement existant.
Chaque prediction consomme le snapshot deja persistee (consigne section 17).
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Application, FeatureSnapshot


class FeatureSnapshotRepository:
    """Acces persistant aux feature snapshots (creation seule + lecture)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        application_id: uuid.UUID,
        feature_set_id: Optional[str],
        feature_schema_version: Optional[str],
        features_json: Optional[dict],
        input_snapshot_hash: Optional[str],
    ) -> FeatureSnapshot:
        snapshot = FeatureSnapshot(
            application_id=application_id,
            feature_set_id=feature_set_id,
            feature_schema_version=feature_schema_version,
            features_json=features_json,
            input_snapshot_hash=input_snapshot_hash,
        )
        self._db.add(snapshot)
        return snapshot

    def get_for_application(
        self, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> Optional[FeatureSnapshot]:
        """Retourne le snapshot le plus recent de l'application (scope tenant)."""
        stmt = (
            select(FeatureSnapshot)
            .join(Application, Application.application_id == FeatureSnapshot.application_id)
            .where(
                FeatureSnapshot.application_id == application_id,
                Application.institution_id == institution_id,
            )
            .order_by(FeatureSnapshot.created_at.desc())
        )
        return self._db.scalar(stmt)

    def get_by_id(
        self, snapshot_id: uuid.UUID, institution_id: uuid.UUID
    ) -> Optional[FeatureSnapshot]:
        stmt = (
            select(FeatureSnapshot)
            .join(Application, Application.application_id == FeatureSnapshot.application_id)
            .where(
                FeatureSnapshot.feature_snapshot_id == snapshot_id,
                Application.institution_id == institution_id,
            )
        )
        return self._db.scalar(stmt)