from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.models.database import DecisionPolicy


class DecisionPolicyService:
    def __init__(self, db: Session):
        self.db = db

    def get_active_policy(
        self, institution_id: uuid.UUID, product_id: str
    ) -> DecisionPolicy | None:
        now = datetime.now(UTC)
        return (
            self.db.query(DecisionPolicy)
            .filter(
                DecisionPolicy.institution_id == institution_id,
                DecisionPolicy.product_id == product_id,
                DecisionPolicy.status == "ACTIVE",
                DecisionPolicy.effective_from <= now,
                (DecisionPolicy.effective_to.is_(None) | (DecisionPolicy.effective_to > now)),
            )
            .first()
        )

    def create(
        self, institution_id: uuid.UUID, product_id: str, rules: dict[str, Any]
    ) -> DecisionPolicy:
        policy = DecisionPolicy(
            institution_id=institution_id,
            product_id=product_id,
            eligibility_rules=rules.get("eligibility", "{}"),
            approve_rule=rules.get("approve", "{}"),
            review_rule=rules.get("review", "{}"),
            decline_rule=rules.get("decline", "{}"),
            effective_from=datetime.now(UTC),
            status="DRAFT",
        )
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy
