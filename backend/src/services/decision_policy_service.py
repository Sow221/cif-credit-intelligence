"""Decision policy service (P0, etape 14).

Encapitule la structure d'une decision policy versionnee : eligibility_rules,
approve_rule, review_rule, decline_rule, fallback_rules avec version,
effective_from/effective_to et status.

Les SEUILS ne sont pas hardcodes dans le code : ils vivent dans le decision
policy (config versionnee). Ce service resolve la policy ACTIVE d'une
institution/product et expose des accesseurs typés aux seuils. S'il n'existe
aucune policy active, on NE retombe pas sur des seuils arbitraires : on signale
que la decision est indisponible (configuration manquante).
"""

import uuid
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.orm import Session

from src.db.models import DecisionPolicy
from src.repositories.decision_policy_repository import DecisionPolicyRepository


class DecisionPolicyNotFound(ValueError):
    """Levee lorsqu'aucune policy active n'est resolue pour la demande."""


class DecisionPolicyService:
    """Resolution des decision policies et de leurs regles."""

    def __init__(self, db: Session) -> None:
        self._repo = DecisionPolicyRepository(db)

    def resolve(
        self,
        institution_id: uuid.UUID,
        product_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> DecisionPolicy:
        """Retourne la policy ACTIVE en vigueur (leve si aucune)."""
        policy = self._repo.get_active(institution_id, product_id, now)
        if policy is None:
            raise DecisionPolicyNotFound(
                "Aucune decision policy active pour cette institution/produit."
            )
        return policy

    # ------------------------------------------------------------------- regles

    def approve_seuils(self, policy: DecisionPolicy) -> Dict[str, float]:
        """Seuils de la regle 'approve' (provenant UNIQUEMENT du policy)."""
        rule = policy.approve_rule or {}
        return {
            "max_pd": self._required(rule, "max_pd"),
            "max_uncertainty": self._required(rule, "max_uncertainty"),
        }

    def review_seuils(self, policy: DecisionPolicy) -> Dict[str, float]:
        """Seuils de la regle 'review' (provenant UNIQUEMENT du policy)."""
        rule = policy.review_rule or {}
        return {
            "max_pd": self._required(rule, "max_pd"),
            "max_uncertainty": self._required(rule, "max_uncertainty"),
        }

    def decline_seuils(self, policy: DecisionPolicy) -> Dict[str, float]:
        """Seuils de la regle 'decline' (provenant UNIQUEMENT du policy)."""
        rule = policy.decline_rule or {}
        return {"max_pd": self._required(rule, "max_pd")}

    def _required(self, rule: Dict, key: str) -> float:
        """Oblige a definir le seuil dans le policy ; jamais de repli arbitraire."""
        if key not in rule:
            raise DecisionPolicyNotFound(f"Seuil '{key}' manquant dans le decision policy.")
        return float(rule[key])

    def eligibility_rules(self, policy: DecisionPolicy) -> Dict:
        return policy.eligibility_rules or {}

    def fallback_rules(self, policy: DecisionPolicy) -> Dict:
        return policy.fallback_rules or {}

    def build_default_policy(
        self,
        *,
        institution_id: uuid.UUID,
        product_id: Optional[str],
        version: str = "1",
        approved_by: Optional[str] = None,
    ) -> DecisionPolicy:
        """Cree une policy DRAFT explicite (thresholds documentes, non hardcodes
        au niveau du moteur : ils restent dans la config de la policy)."""
        now = datetime.utcnow()
        return self._repo.create(
            institution_id=institution_id,
            product_id=product_id,
            version=version,
            eligibility_rules={
                "min_monthly_income": 50000.0,
                "min_seniority_months": 3,
            },
            approve_rule={"max_pd": 0.30, "max_uncertainty": 0.35},
            review_rule={"max_pd": 0.55, "max_uncertainty": 0.70},
            decline_rule={"max_pd": 0.55},
            fallback_rules={"on_unavailable": "REVIEW"},
            effective_from=now,
            effective_to=None,
            status="DRAFT",
            approved_by=approved_by,
        )