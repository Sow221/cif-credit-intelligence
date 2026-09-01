"""Repository des profils d'information (P0, etape 8).

La table information_profiles ne porte pas de colonne institution : le scope
tenant est applique par jointure avec la table `applications` (multi-tenancy),
comme pour application_data et data_lineage.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Application, InformationProfile


class InformationProfileRepository:
    """Acces persistant aux profils d'information (scope tenant)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        application_id: uuid.UUID,
        applicant_status: str,
        credit_depth: str,
        financial_depth: str,
        business_depth: str,
        relationship_depth: str,
        data_quality: str,
        information_state: str,
        profile_version: str,
        details_json: Optional[dict] = None,
    ) -> InformationProfile:
        profile = InformationProfile(
            application_id=application_id,
            applicant_status=applicant_status,
            credit_depth=credit_depth,
            financial_depth=financial_depth,
            business_depth=business_depth,
            relationship_depth=relationship_depth,
            data_quality=data_quality,
            information_state=information_state,
            profile_version=profile_version,
            details_json=details_json,
        )
        self._db.add(profile)
        return profile

    def get_for_application(
        self, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> Optional[InformationProfile]:
        """Retourne le dernier profil de l'application (scope tenant)."""
        stmt = (
            select(InformationProfile)
            .join(Application, Application.application_id == InformationProfile.application_id)
            .where(
                InformationProfile.application_id == application_id,
                Application.institution_id == institution_id,
            )
            .order_by(InformationProfile.created_at.desc())
        )
        return self._db.scalar(stmt)
