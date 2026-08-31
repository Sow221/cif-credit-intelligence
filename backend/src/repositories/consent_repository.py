"""Repository des consentements (P0, etape 6).

Le scope institution est applique directement via la colonne
consents.institution_id (multi-tenancy).
"""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Consent


class ConsentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_client(
        self, client_id: uuid.UUID, institution_id: uuid.UUID
    ) -> List[Consent]:
        stmt = (
            select(Consent)
            .where(
                Consent.client_id == client_id,
                Consent.institution_id == institution_id,
            )
            .order_by(Consent.created_at.desc())
        )
        return list(self._db.scalars(stmt).all())

    def get(self, consent_id: uuid.UUID, institution_id: uuid.UUID) -> Optional[Consent]:
        stmt = select(Consent).where(
            Consent.consent_id == consent_id,
            Consent.institution_id == institution_id,
        )
        return self._db.scalar(stmt)
