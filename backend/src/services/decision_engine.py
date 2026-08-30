"""Moteur de decision.

Combine la probability of default (PD), le niveau de confiance et le flag
thin-file pour produire une recommandation reglementee :
APPROBATION / REVUE_HUMAINE / AJUSTEMENT / REFUS.
"""

from typing import ClassVar


class DecisionEngine:
    """Applique la table de decision (regles R1-R6)."""

    THRESHOLDS: ClassVar[dict] = {
        "approve_max": 0.10,
        "review_max": 0.25,
        "adjust_max": 0.45,
    }

    def evaluate(
        self,
        pd_score: float,
        confidence_level: str,
        is_thin_file: bool,
        n_past_loans: int,
    ) -> dict:
        """Produit la decision et sa justification.

        Args:
            pd_score: probability of default dans [0, 1].
            confidence_level: FAIBLE, MOYENNE ou ELEVEE.
            is_thin_file: client sans historique exploitable.
            n_past_loans: nombre de prets historiques (recupere ici pour la
                tracabilite future).

        Returns:
            dict avec "decision" et "raison".
        """
        # R1 : Thin-File -> REVUE HUMAINE
        if is_thin_file:
            return {"decision": "REVUE_HUMAINE", "raison": "Client sans historique"}

        # R2 : Confiance faible -> REVUE HUMAINE
        if confidence_level == "FAIBLE":
            return {"decision": "REVUE_HUMAINE", "raison": "Confiance insuffisante"}

        # R3-R6 : Seuils de PD
        if pd_score <= self.THRESHOLDS["approve_max"]:
            return {
                "decision": "APPROBATION",
                "raison": f"PD={pd_score:.3f} <= 0.10",
            }
        if pd_score <= self.THRESHOLDS["review_max"]:
            return {
                "decision": "REVUE_HUMAINE",
                "raison": f"0.10 < PD={pd_score:.3f} <= 0.25",
            }
        if pd_score <= self.THRESHOLDS["adjust_max"]:
            return {
                "decision": "AJUSTEMENT",
                "raison": f"0.25 < PD={pd_score:.3f} <= 0.45",
            }
        return {
            "decision": "REFUS",
            "raison": f"PD={pd_score:.3f} > 0.45",
        }
