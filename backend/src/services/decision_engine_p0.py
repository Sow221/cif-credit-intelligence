"""Decision engine (P0, etape 15).

Moteur de decision METIER aligne sur le decision_policy (etape 14). Les trois
decisions metier sont APPROVE / REVIEW / DECLINE (consigne section 28).

Entrees (consigne section 28) :
    eligibility, pd_calibrated, uncertainty, information_state, data_quality,
    decision_policy

AJUSTEMENT n'est PLUS une quatrieme decision par defaut (consigne section 31) :
si un montant/duree differents doivent etre recommandes, `proposed_terms` est
renvoye SEPAREMENT de `decision`.

Les SEUILS proviennent du decision policy (config versionnee) ; ils ne sont
jamais hardcodes dans ce moteur.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Decision(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    DECLINE = "DECLINE"


@dataclass
class EngineInput:
    """Entrees structurees du moteur de decision."""

    eligibility: bool
    pd_calibrated: float
    uncertainty_level: str
    uncertainty_score: float
    information_state: Optional[str] = None
    data_quality: Optional[str] = None
    approve_max_pd: Optional[float] = None
    decline_max_pd: Optional[float] = None
    approve_max_uncertainty: Optional[float] = None


@dataclass
class EngineResult:
    """Sortie metier du moteur."""

    decision: Decision
    reason: str
    proposed_terms: Optional[Dict] = field(default_factory=dict)


class DecisionEngineP0:
    """Applique les regles du policy a une candidature eligible."""

    def decide(self, inp: EngineInput) -> EngineResult:
        # R1 : ineligible -> DECLINE (decision metier, sans terms).
        if not inp.eligibility:
            return EngineResult(
                decision=Decision.DECLINE,
                reason="candidature ineligible",
                proposed_terms=None,
            )

        # R2 : les seuils doivent etre fournis par le policy (jamais hardcodes).
        if (
            inp.approve_max_pd is None
            or inp.decline_max_pd is None
            or inp.approve_max_uncertainty is None
        ):
            raise ValueError("Seuils de decision manquants (policy non resolu).")

        # R3 : incertitude elevee -> REVIEW (ne pas trancher un cas incertain).
        if inp.uncertainty_level.upper() == "HIGH":
            return EngineResult(
                decision=Decision.REVIEW,
                reason="incertitude elevee",
            )

        # R4 : donnnees pauvres -> REVIEW (information insuffisante).
        state = (inp.information_state or "").upper()
        quality = (inp.data_quality or "").upper()
        if state in ("NO_FILE", "DATA_POOR") or quality in ("LOW", "NONE"):
            return EngineResult(
                decision=Decision.REVIEW,
                reason=f"information insuffisante (state={state or '?'} quality={quality or '?'})",
            )

        # R5 : approbation (pd bas + incertitude basse).
        if inp.pd_calibrated <= inp.approve_max_pd:
            if inp.uncertainty_score <= inp.approve_max_uncertainty:
                return EngineResult(
                    decision=Decision.APPROVE,
                    reason=f"pd={inp.pd_calibrated:.3f} <= {inp.approve_max_pd}",
                )
            return EngineResult(
                decision=Decision.REVIEW,
                reason="incertitude moyenne malgre un PD faible",
            )

        # R6 : refus franc au-dela du seuil de decline.
        if inp.pd_calibrated > inp.decline_max_pd:
            return EngineResult(
                decision=Decision.DECLINE,
                reason=f"pd={inp.pd_calibrated:.3f} > {inp.decline_max_pd}",
            )

        # R7 : zone mediane -> REVIEW.
        return EngineResult(
            decision=Decision.REVIEW,
            reason=f"pd={inp.pd_calibrated:.3f} dans la zone d'examen",
        )