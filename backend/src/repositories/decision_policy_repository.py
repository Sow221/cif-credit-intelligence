"""Repository des decision policies (P0, etape 14).

La table decision_policies porte institution_id et product_id. Le scope tenant
est applique directement par la colonne institution_id (multi-tenancy).

Une policy est versionnee et bornee par effective_from/effective_to + status :
seule une policy ACTIVE et en vigueur est resolue pour une demande.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import DecisionPolicy


class DecisionPolicyRepository:
    """Acces persistant aux decision policies."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        institution_id: uuid.UUID,
        product_id: Optional[str],
        version: str,
        eligibility_rules: Optional[dict],
        approve_rule: Optional[dict],
        review_rule: Optional[dict],
        decline_rule: Optional[dict],
        fallback_rules: Optional[dict],
        effective_from: Optional[datetime],
        effective_to: Optional[datetime],
        status: str = "DRAFT",
        approved_by: Optional[str] = None,
    ) -> DecisionPolicy:
        policy = DecisionPolicy(
            institution_id=institution_id,
            product_id=product_id,
            version=version,
            eligibility_rules=eligibility_rules,
            approve_rule=approve_rule,
            review_rule=review_rule,
            decline_rule=decline_rule,
            fallback_rules=fallback_rules,
            effective_from=effective_from,
            effective_to=effective_to,
            status=status,
            approved_by=approved_by,
        )
        self._db.add(policy)
        return policy

    def get_active(
        self,
        institution_id: uuid.UUID,
        product_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> Optional[DecisionPolicy]:
        """Resout la policy ACTIVE en vigueur pour une institution/product."""
        now = now or datetime.utcnow()
        stmt = (
            select(DecisionPolicy)
            .where(
                DecisionPolicy.institution_id == institution_id,
                DecisionPolicy.status == "ACTIVE",
                DecisionPolicy.effective_from.is_(None)
                | (DecisionPolicy.effective_from <= now),
                DecisionPolicy.effective_to.is_(None)
                | (DecisionPolicy.effective_to >= now),
            )
            .order_by(DecisionPolicy.created_at.desc())
        )
        if product_id:
            stmt = stmt.where(
                (DecisionPolicy.product_id == product_id)
                | (DecisionPolicy.product_id.is_(None))
            )
        return self._db.scalar(stmt)

    def get_by_id(self, policy_id: uuid.UUID) -> Optional[DecisionPolicy]:
        stmt = select(DecisionPolicy).where(DecisionPolicy.policy_id == policy_id)
        return self._db.scalar(stmt)