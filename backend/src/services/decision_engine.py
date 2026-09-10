from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DecisionInput:
    eligible: bool
    pd_calibrated: float
    uncertainty_level: str
    information_state: str
    data_quality: str
    policy: dict[str, Any]


@dataclass
class DecisionOutput:
    recommendation: str
    proposed_amount: float | None = None
    proposed_term: int | None = None
    reason: str = ""


class DecisionEngine:
    def decide(self, inputs: DecisionInput) -> DecisionOutput:
        if not inputs.eligible:
            return DecisionOutput(recommendation="DECLINE", reason="Non éligible")
        if inputs.uncertainty_level == "HIGH":
            return DecisionOutput(recommendation="REVIEW", reason="Incertitude élevée")
        if inputs.information_state in ("NO_FILE", "THIN_FILE"):
            return DecisionOutput(recommendation="REVIEW", reason="Informations insuffisantes")
        if inputs.data_quality in ("FAIL", "POOR"):
            return DecisionOutput(recommendation="REVIEW", reason="Qualité données insuffisante")
        approve_threshold = inputs.policy.get("approve_threshold", 0.7)
        decline_threshold = inputs.policy.get("decline_threshold", 0.3)
        if inputs.pd_calibrated <= decline_threshold:
            return DecisionOutput(recommendation="DECLINE", reason="Risque trop élevé")
        if inputs.pd_calibrated >= approve_threshold:
            return DecisionOutput(recommendation="APPROVE", reason="Risque acceptable")
        return DecisionOutput(recommendation="REVIEW", reason="Zone grise - revue nécessaire")
