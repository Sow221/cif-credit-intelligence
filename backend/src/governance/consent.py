"""Gouvernance du consentement (P0, etape 6).

Le guard CONSENT empeche l'utilisation d'une donnee lorsque son consentement
obligatoire n'est pas valide.

Statuts (table consents) :
    GRANTED, REFUSED, REVOKED, NOT_REQUIRED, UNKNOWN

Une donnee n'est utilisable que si le consentement associe est GRANTED ou si
la donnee est declaree NOT_REQUIRED. Tout autre etat (REFUSED, REVOKED,
UNKNOWN, ou absence de consentement) rend la donnee inutilisable.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.audit.audit_service import AuditEventType, AuditService
from src.core.exceptions import ConsentRefusedError, ConsentRequiredError
from src.db.models import Consent


class ConsentStatus(str, Enum):
    GRANTED = "GRANTED"
    REFUSED = "REFUSED"
    REVOKED = "REVOKED"
    NOT_REQUIRED = "NOT_REQUIRED"
    UNKNOWN = "UNKNOWN"


# Statuts rendant la donnee utilisable.
ALLOWED_STATUSES: frozenset[ConsentStatus] = frozenset(
    {ConsentStatus.GRANTED, ConsentStatus.NOT_REQUIRED}
)


class ConsentCheck(BaseModel):
    """Resultat de la verification du consentement."""

    allowed: bool
    status: str
    reason: str


class ConsentGuard:
    """Verifie qu'une donnee dispose d'un consentement valide."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def check(
        self,
        *,
        client_id: uuid.UUID,
        institution_id: uuid.UUID,
        source_id: Optional[uuid.UUID] = None,
        purpose: Optional[str] = None,
    ) -> ConsentCheck:
        """Retourne si la donnee est utilisable selon le consentement courant."""
        consent = self._latest(client_id, institution_id, source_id, purpose)
        if consent is None:
            return ConsentCheck(
                allowed=False,
                status=ConsentStatus.UNKNOWN.value,
                reason="Aucun consentement enregistre pour cette donnee",
            )
        status = ConsentStatus(consent.status)
        if status in ALLOWED_STATUSES:
            return ConsentCheck(
                allowed=True,
                status=status.value,
                reason=f"Consentement {status.value} valide",
            )
        return ConsentCheck(
            allowed=False,
            status=status.value,
            reason=f"Consentement {status.value} : donnee inutilisable",
        )

    def assert_allowed(self, check: ConsentCheck) -> None:
        """Leve une erreur si la donnee ne doit pas etre utilisee."""
        if not check.allowed:
            if check.status == ConsentStatus.REFUSED.value:
                raise ConsentRefusedError(
                    "Consentement refuse pour cette donnee", details={"status": check.status}
                )
            raise ConsentRequiredError(
                "Consentement obligatoire manquant ou invalide",
                details={"status": check.status},
            )

    def _latest(
        self,
        client_id: uuid.UUID,
        institution_id: uuid.UUID,
        source_id: Optional[uuid.UUID],
        purpose: Optional[str],
    ) -> Optional[Consent]:
        stmt = select(Consent).where(
            Consent.client_id == client_id,
            Consent.institution_id == institution_id,
        )
        if source_id is not None:
            stmt = stmt.where(Consent.source_id == source_id)
        if purpose is not None:
            stmt = stmt.where(Consent.purpose == purpose)
        stmt = stmt.order_by(Consent.created_at.desc())
        return self._db.scalar(stmt)


class ConsentService:
    """Gestion du cycle de vie d'un consentement (grant / revoke)."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._guard = ConsentGuard(db)
        self._audit = AuditService(db)

    def record(
        self,
        *,
        client_id: uuid.UUID,
        institution_id: uuid.UUID,
        status: ConsentStatus,
        purpose: str,
        source_id: Optional[uuid.UUID] = None,
        version: str = "1",
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Consent:
        """Enregistre un consentement (grant, refuse, revoke, not_required)."""
        now = datetime.utcnow()
        consent = Consent(
            client_id=client_id,
            institution_id=institution_id,
            source_id=source_id,
            purpose=purpose,
            status=status.value,
            version=version,
            granted_at=now if status == ConsentStatus.GRANTED else None,
            revoked_at=now if status == ConsentStatus.REVOKED else None,
        )
        self._db.add(consent)
        self._db.flush()
        self._audit.log(
            AuditEventType.CONSENT_CHANGED,
            institution_id=institution_id,
            actor_id=actor_id,
            entity_type="consent",
            entity_id=str(consent.consent_id),
            request_id=request_id,
            details={"status": status.value, "purpose": purpose},
        )
        self._db.commit()
        self._db.refresh(consent)
        return consent

    def check(
        self,
        *,
        client_id: uuid.UUID,
        institution_id: uuid.UUID,
        source_id: Optional[uuid.UUID] = None,
        purpose: Optional[str] = None,
    ) -> ConsentCheck:
        return self._guard.check(
            client_id=client_id,
            institution_id=institution_id,
            source_id=source_id,
            purpose=purpose,
        )
