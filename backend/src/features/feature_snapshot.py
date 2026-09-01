"""Feature snapshot (P0, etape 10).

Cree un snapshot IMMUABLE des features avant toute prediction (consigne
section 17) : feature_set_id, feature_schema_version, features_json et
input_snapshot_hash. Une prediction ne recalcule jamais un ancien snapshot
avec le code actuel : elle consomme celui deja persiste.

Le snapshot est rattache au feature set resolu par le feature engine (etape 9),
lui-meme derive du profil d'information (etape 8).
"""

import hashlib
import json
import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.core.exceptions import NotFoundError
from src.features.feature_engine import DEFAULT_CATALOG, FeatureSet, resolve_feature_set
from src.features.information_profiler import InformationProfilerService
from src.repositories.application_repository import ApplicationRepository
from src.repositories.feature_snapshot_repository import FeatureSnapshotRepository


class FeatureSnapshotInput(BaseModel):
    """Entree d'un calcul de features (brutes, non calculees)."""

    model_config = ConfigDict(extra="forbid")

    application_id: uuid.UUID
    # Valeurs deja connues pour la candidature (champ -> valeur).
    values: Dict[str, object] = Field(default_factory=dict)
    # Version du schema de features attendu (snapshot verrouille).
    feature_schema_version: str = "1"


class FeatureSnapshotResult(BaseModel):
    """Resultat du snapshot immuable cree."""

    model_config = ConfigDict(extra="forbid")

    feature_snapshot_id: uuid.UUID
    application_id: uuid.UUID
    feature_set_id: str
    feature_schema_version: str
    features: Dict[str, object]
    input_snapshot_hash: str


def compute_snapshot_hash(
    application_id: uuid.UUID,
    feature_set_id: str,
    feature_schema_version: str,
    features: Dict[str, object],
) -> str:
    """Hash SHA-256 deterministe (canonical JSON) de l'input du snapshot."""
    payload = {
        "application_id": str(application_id),
        "feature_set_id": feature_set_id,
        "feature_schema_version": feature_schema_version,
        "features": features,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class FeatureSnapshotService:
    """Orchestre la creation et la consultation d'un snapshot immuable."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._snapshots = FeatureSnapshotRepository(db)
        self._apps = ApplicationRepository(db)
        self._profiler = InformationProfilerService(db)
        self._audit = AuditService(db)
        self._catalog = DEFAULT_CATALOG

    def build_snapshot(
        self,
        *,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        feature_schema_version: str = "1",
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> FeatureSnapshotResult:
        application = self._apps.get(application_id, institution_id)
        if application is None:
            raise NotFoundError(f"Application {application_id} introuvable")

        # Feature set resolu depuis le profil d'information de la candidature.
        profile = self._profiler.build_profile(
            application_id=application_id,
            institution_id=institution_id,
            actor_id=actor_id,
            request_id=request_id,
        )
        feature_set = resolve_feature_set(profile.information_state)
        features = self._compute_features(application_id, institution_id, feature_set)

        snapshot_hash = compute_snapshot_hash(
            application_id=application_id,
            feature_set_id=feature_set.code,
            feature_schema_version=feature_schema_version,
            features=features,
        )

        model = self._snapshots.create(
            application_id=application_id,
            feature_set_id=feature_set.code,
            feature_schema_version=feature_schema_version,
            features_json=features,
            input_snapshot_hash=snapshot_hash,
        )
        self._db.flush()
        snapshot_id = model.feature_snapshot_id
        self._db.commit()

        self._audit.log(
            AuditEventType.FEATURE_SNAPSHOT_CREATED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="application",
            entity_id=str(application_id),
            request_id=request_id,
            details={
                "feature_set_id": feature_set.code,
                "feature_schema_version": feature_schema_version,
                "input_snapshot_hash": snapshot_hash,
                "feature_count": len(features),
            },
        )
        return FeatureSnapshotResult(
            feature_snapshot_id=snapshot_id,
            application_id=application_id,
            feature_set_id=feature_set.code,
            feature_schema_version=feature_schema_version,
            features=features,
            input_snapshot_hash=snapshot_hash,
        )

    def get_snapshot(
        self,
        application_id: uuid.UUID,
        snapshot_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> Optional[FeatureSnapshotResult]:
        model = self._snapshots.get_by_id(snapshot_id, institution_id)
        if model is None or model.application_id != application_id:
            return None
        return FeatureSnapshotResult(
            feature_snapshot_id=model.feature_snapshot_id,
            application_id=model.application_id,
            feature_set_id=model.feature_set_id or "",
            feature_schema_version=model.feature_schema_version or "1",
            features=model.features_json or {},
            input_snapshot_hash=model.input_snapshot_hash or "",
        )

    def get_latest(
        self,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
    ) -> Optional[FeatureSnapshotResult]:
        model = self._snapshots.get_for_application(application_id, institution_id)
        if model is None:
            return None
        return self.get_snapshot(
            application_id=application_id,
            snapshot_id=model.feature_snapshot_id,
            institution_id=institution_id,
        )

    # ------------------------------------------------------------------- interne

    def _compute_features(
        self,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        feature_set: FeatureSet,
    ) -> Dict[str, object]:
        """Calcule les features de base pour le set resolu.

        Version 1 : features presentes dans les donnees ingerees => valeur
        brute ; sinon None. La formule de derivation du modele est appliquee
        par le risk engine (etape 11) ; le snapshot fige l'input brut tel quel.
        """
        features: Dict[str, object] = {}
        for feature in feature_set.feature_ids():
            value = self._feature_value(application_id, institution_id, feature)
            features[feature] = value
        return features

    def _feature_value(
        self,
        application_id: uuid.UUID,
        institution_id: uuid.UUID,
        feature_name: str,
    ) -> Optional[object]:
        """Recupere la valeur brute du feature candidat (le plus recent)."""
        row = self._db.execute(
            text(
                "SELECT field_value FROM application_data ad "
                "JOIN applications a ON a.application_id = ad.application_id "
                "WHERE a.application_id = :aid AND a.institution_id = :iid "
                "AND ad.field_name = :f "
                "ORDER BY ad.created_at DESC LIMIT 1"
            ),
            {"aid": str(application_id), "iid": str(institution_id), "f": feature_name},
        ).fetchone()
        if row is None:
            return None
        return row[0]