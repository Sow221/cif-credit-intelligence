"""Savings-to-income ratio feature.

Formula: savings / (income + 1)
"""

from typing import Any, Dict


class SavingsRatioFeature:
    """Computes the savings-to-income ratio from raw inputs."""

    name = "savings_to_income_ratio"

    @staticmethod
    def compute(inputs: Dict[str, Any]) -> float:
        savings = float(inputs.get("current_savings", 0.0))
        income = float(inputs.get("monthly_income", 0.0))
        return savings / (income + 1.0)
