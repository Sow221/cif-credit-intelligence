from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass
class FeatureDefinition:
    name: str
    data_type: str
    feature_group: str
    status: str = "APPROVED"


APPROVED_FEATURES = [
    FeatureDefinition("monthly_income", "float", "financial"),
    FeatureDefinition("monthly_expenses", "float", "financial"),
    FeatureDefinition("savings_balance", "float", "financial"),
    FeatureDefinition("loan_count", "int", "credit"),
    FeatureDefinition("active_loans", "int", "credit"),
    FeatureDefinition("total_debt", "float", "credit"),
    FeatureDefinition("payment_history_ratio", "float", "credit"),
    FeatureDefinition("days_since_last_loan", "int", "credit"),
    FeatureDefinition("business_age_months", "int", "business"),
    FeatureDefinition("monthly_revenue", "float", "business"),
    FeatureDefinition("sector", "str", "business"),
    FeatureDefinition("zone", "str", "business"),
    FeatureDefinition("client_age_days", "int", "relationship"),
    FeatureDefinition("previous_applications", "int", "relationship"),
    FeatureDefinition("savings_frequency", "float", "financial"),
    FeatureDefinition("income_stability", "float", "financial"),
    FeatureDefinition("debt_to_income", "float", "credit"),
    FeatureDefinition("loan_amount_avg", "float", "credit"),
    FeatureDefinition("repayment_rate", "float", "credit"),
    FeatureDefinition("guarantee_type", "str", "credit"),
    FeatureDefinition("business_type", "str", "business"),
    FeatureDefinition("employee_count", "int", "business"),
    FeatureDefinition("monthly_turnover", "float", "business"),
    FeatureDefinition("account_age_days", "int", "relationship"),
    FeatureDefinition("transaction_count", "int", "financial"),
]

FEATURE_SETS = {
    "MINIMAL": ["monthly_income", "savings_balance", "loan_count", "business_age_months", "zone"],
    "BUSINESS": [
        "monthly_income",
        "monthly_expenses",
        "savings_balance",
        "business_age_months",
        "monthly_revenue",
        "sector",
        "zone",
        "business_type",
        "employee_count",
        "monthly_turnover",
    ],
    "FINANCIAL": [
        "monthly_income",
        "monthly_expenses",
        "savings_balance",
        "savings_frequency",
        "income_stability",
        "transaction_count",
        "account_age_days",
    ],
    "CREDIT": [
        "loan_count",
        "active_loans",
        "total_debt",
        "payment_history_ratio",
        "days_since_last_loan",
        "debt_to_income",
        "loan_amount_avg",
        "repayment_rate",
        "guarantee_type",
    ],
    "ALTERNATIVE": ["client_age_days", "previous_applications", "zone", "sector"],
    "FULL_ADMISSIBLE": [f.name for f in APPROVED_FEATURES],
}


class FeatureEngineService:
    def __init__(self) -> None:
        self.features = {f.name: f for f in APPROVED_FEATURES}

    def resolve_feature_set(self, set_name: str) -> list[str]:
        if set_name not in FEATURE_SETS:
            raise ValueError(f"Feature set inconnu: {set_name}")
        return FEATURE_SETS[set_name]

    def build_features(
        self, raw_data: dict[str, Any], feature_set: str = "FULL_ADMISSIBLE"
    ) -> dict[str, Any]:
        feature_names = self.resolve_feature_set(feature_set)
        features = {}
        for name in feature_names:
            features[name] = raw_data.get(name, 0.0)
        return features

    def compute_snapshot_hash(self, features: dict[str, Any]) -> str:
        canonical = json.dumps(features, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()
