"""Repository de l'application (P0, etape 2).

Encapsule les acces PostgreSQL sur la table applications, scope tenant.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Application


class ApplicationRepository:
    """Acces CRUD sur l'entite Application, scope tenant."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        institution_id: uuid.UUID,
        client_id: uuid.UUID,
        product_id: str,
        requested_amount: float,
        currency: str,
        requested_term: Optional[int],
        purpose: Optional[str],
    ) -> Application:
        application = Application(
            institution_id=institution_id,
            client_id=client_id,
            product_id=product_id,
            requested_amount=requested_amount,
            currency=currency,
            requested_term=requested_term,
            purpose=purpose,
            status="DRAFT",
        )
        self._db.add(application)
        return application

    def get(
        self, application_id: uuid.UUID, institution_id: uuid.UUID
    ) -> Optional[Application]:
        return (
            self._db.execute(
                select(Application).where(
                    Application.application_id == application_id,
                    Application.institution_id == institution_id,
                )
            )
            .scalars()
            .first()
        )

    def list(self, institution_id: uuid.UUID) -> list[Application]:
        return list(
            self._db.execute(
                select(Application)
                .where(Application.institution_id == institution_id)
                .order_by(Application.created_at.desc())
            )
            .scalars()
            .all()
        )

    def update_status(self, application: Application, status: str) -> Application:
        application.status = status
        return application
