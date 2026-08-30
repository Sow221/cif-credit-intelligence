"""Loan-to-savings ratio feature.

Formula: request / (savings + 1)
"""

import math
from typing import Any, Dict


class LoanToSavingsFeature:
    """Computes the loan-to-savings ratio from raw inputs."""

    name = "loan_to_savings_ratio"

    @staticmethod
    def compute(inputs: Dict[str, Any]) -> float:
        request = float(inputs.get("current_loan_request", 0.0))
        savings = float(inputs.get("current_savings", 0.0))
        return request / (savings + 1.0)
