"""Central feature registry.

Reference unique des 25 features du modele officiel (MODEL_OFFICIAL.joblib).
Extrait depuis `MODEL_OFFICIAL.joblib.feature_names_in_`.

Chaque feature est decrite avec :
- name : nom exact attendu par le modele
- kind : RAW (colonne directe) | DERIVED (calculee)
- formula : formule de calcul documentee
- derive_from : inputs bruts necessaires au calcul (si DERIVED)
"""

from typing import Dict, List


# Formules documentees (reponse.txt, Partie 1.2)
FORMULAS: Dict[str, str] = {
    "age": "Direct",
    "seniority_months": "Direct",
    "monthly_income": "Direct",
    "current_savings": "Direct",
    "avg_savings_24m": "Moyenne des 24 soldes mensuels",
    "savings_std_24m": "Ecart-type des 24 soldes",
    "savings_volatility": "std / (avg + 1)",
    "savings_stability": "clip(0.5 + risk_factor * 0.35, 0.05, 0.95)",
    "n_past_loans": "Direct",
    "current_loan_request": "Direct",
    "current_loan_duration": "Direct",
    "loan_to_savings_ratio": "request / (savings + 1)",
    "n_loans": "Nombre de prets historiques",
    "avg_loan_amount": "Moyenne des montants des prets passes",
    "total_loan_amount": "Somme des montants des prets passes",
    "avg_repayment_regularity": "Moyenne des regularites",
    "min_repayment_regularity": "Minimum des regularites",
    "max_historical_dpd": "Maximum des retards (Days Past Due)",
    "mean_historical_dpd": "Moyenne des retards",
    "n_defaults": "Nombre de defauts passes",
    "loan_to_income_ratio": "request / (income + 1)",
    "historical_default_rate": "n_defaults / (n_loans + 1)",
    "savings_to_income_ratio": "savings / (income + 1)",
    "seniority_years": "months / 12",
    "overall_payment_regularity": "n_loans * avg_reg / (n_loans + 1)",
}

# Features derives (calculees dans definitions/)
DERIVED_FEATURES: Dict[str, str] = {
    "loan_to_savings_ratio": "definitions.loan_to_savings.LoanToSavingsFeature",
    "loan_to_income_ratio": "definitions.loan_to_income.LoanToIncomeFeature",
    "savings_to_income_ratio": "definitions.savings_ratio.SavingsRatioFeature",
    "seniority_years": "definitions.seniority.SeniorityFeature",
}


class FeatureRegistry:
    """Registre central des features du modele."""

    # Les 25 features exactes du modele officiel (ordre d'entrainement).
    FEATURES: List[str] = [
        "age",
        "seniority_months",
        "monthly_income",
        "current_savings",
        "avg_savings_24m",
        "savings_std_24m",
        "savings_volatility",
        "savings_stability",
        "n_past_loans",
        "current_loan_request",
        "current_loan_duration",
        "loan_to_savings_ratio",
        "n_loans",
        "avg_loan_amount",
        "total_loan_amount",
        "avg_repayment_regularity",
        "min_repayment_regularity",
        "max_historical_dpd",
        "mean_historical_dpd",
        "n_defaults",
        "loan_to_income_ratio",
        "historical_default_rate",
        "savings_to_income_ratio",
        "seniority_years",
        "overall_payment_regularity",
    ]

    @classmethod
    def all_features(cls) -> List[str]:
        """Retourne la liste complete des features dans l'ordre du modele."""
        return list(cls.FEATURES)

    @classmethod
    def count(cls) -> int:
        return len(cls.FEATURES)

    @classmethod
    def is_derived(cls, feature: str) -> bool:
        return feature in DERIVED_FEATURES

    @classmethod
    def formula(cls, feature: str) -> str:
        return FORMULAS.get(feature, "Inconnue")
