"""Loan-to-income ratio feature.

Formula: request / (income + 1)
"""

from typing import Any, Dict


class LoanToIncomeFeature:
    """Computes the loan-to-income ratio from raw inputs."""

    name = "loan_to_income_ratio"

    @staticmethod
    def compute(inputs: Dict[str, Any]) -> float:
        request = float(inputs.get("current_loan_request", 0.0))
        income = float(inputs.get("monthly_income", 0.0))
        return request / (income + 1.0)
