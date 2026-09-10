from __future__ import annotations

from typing import Any


class RiskEngine:
    def score(self, features: dict[str, Any], model: Any = None) -> float:
        """Score features and return PD. If no model available, use heuristic."""
        if model and hasattr(model, "predict"):
            try:
                import numpy as np

                feature_values = [features.get(f, 0.0) for f in sorted(features.keys())]
                x = np.array([feature_values])
                return float(model.predict(x)[0])
            except Exception:
                pass
        return self._heuristic_score(features)

    def _heuristic_score(self, features: dict[str, Any]) -> float:
        score = 0.5
        dti = features.get("debt_to_income", 0)
        if dti > 0.6:
            score += 0.2
        elif dti > 0.4:
            score += 0.1
        repayment = features.get("repayment_rate", 1.0)
        if repayment < 0.5:
            score += 0.15
        elif repayment < 0.8:
            score += 0.05
        savings = features.get("savings_balance", 0)
        if savings > 100000:
            score -= 0.1
        elif savings > 50000:
            score -= 0.05
        return max(0.01, min(0.99, score))
