"""Seniority feature.

Formula: months / 12
"""

from typing import Any, Dict


class SeniorityFeature:
    """Computes seniority in years from seniority in months."""

    name = "seniority_years"

    @staticmethod
    def compute(inputs: Dict[str, Any]) -> float:
        months = float(inputs.get("seniority_months", 0.0))
        return months / 12.0
