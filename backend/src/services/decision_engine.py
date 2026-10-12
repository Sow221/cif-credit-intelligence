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
        # pd_calibrated = probabilité de DÉFAUT calibrée : plus elle est basse, meilleur est le risque.
        # Seuils alignés sur configs/params.yaml (decision_engine.thresholds) :
        #   pd < approve_max_pd  -> APPROVE
        #   pd >= decline_min_pd -> DECLINE
        #   entre les deux       -> REVIEW (zone grise)
        approve_max_pd = inputs.policy.get("approve_max_pd", 0.05)
        decline_min_pd = inputs.policy.get("decline_min_pd", 0.30)
        if approve_max_pd >= decline_min_pd:
            raise ValueError("approve_max_pd doit être strictement inférieur à decline_min_pd")
        if inputs.pd_calibrated >= decline_min_pd:
            return DecisionOutput(recommendation="DECLINE", reason="Risque trop élevé")
        if inputs.pd_calibrated < approve_max_pd:
            return DecisionOutput(recommendation="APPROVE", reason="Risque acceptable")
        return DecisionOutput(recommendation="REVIEW", reason="Zone grise - revue nécessaire")
