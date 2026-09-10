from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.schemas.eligibility import EligibilityResult


@dataclass
class EligibilityRule:
    name: str
    check: str
    threshold: float | None = None


DEFAULT_RULES = [
    EligibilityRule("min_amount", "requested_amount >= 10000", 10000),
    EligibilityRule("max_amount", "requested_amount <= 5000000", 5000000),
    EligibilityRule("min_term", "requested_term >= 1", 1),
    EligibilityRule("max_term", "requested_term <= 60", 60),
]


class EligibilityService:
    def __init__(self, rules: list[EligibilityRule] | None = None):
        self.rules = rules or DEFAULT_RULES

    def check(self, application_data: dict[str, Any]) -> EligibilityResult:
        reasons = []
        eligible = True
        amount = application_data.get("requested_amount", 0)
        term = application_data.get("requested_term", 0)
        if amount < 10000:
            reasons.append("Montant minimum: 10,000 XOF")
            eligible = False
        if amount > 5000000:
            reasons.append("Montant maximum: 5,000,000 XOF")
            eligible = False
        if term < 1:
            reasons.append("DurÃ©e minimum: 1 mois")
            eligible = False
        if term > 60:
            reasons.append("DurÃ©e maximum: 60 mois")
            eligible = False
        return EligibilityResult(eligible=eligible, reasons=reasons, policy_version="1.0")
