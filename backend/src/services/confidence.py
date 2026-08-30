"""Service de niveau de confiance.

Evalue la fiabilite d'une prediction en fonction de l'epaisseur du dossier
(has_history), du nombre de prets passes et de l'anciennete dans
l'institution (seniority_months).
"""


class ConfidenceService:
    """Calcule le niveau de confiance selon des regles explicites."""

    @staticmethod
    def compute(n_past_loans: int, seniority_months: int, has_history: bool) -> dict:
        """Retourne le niveau et le score de confiance.

        Args:
            n_past_loans: nombre de prets historiques.
            seniority_months: anciennete client en mois.
            has_history: presence d'un historique (client non thin-file).

        Returns:
            dict avec "level" (FAIBLE|MOYENNE|ELEVEE) et "score" dans [0, 1].
        """
        if not has_history:
            return {"level": "FAIBLE", "score": 0.35}

        if n_past_loans >= 3 and seniority_months >= 24:
            return {"level": "ELEVEE", "score": 0.85}
        if n_past_loans >= 1:
            return {"level": "MOYENNE", "score": 0.60}
        return {"level": "FAIBLE", "score": 0.35}
