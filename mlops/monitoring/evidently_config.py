"""Configuration du monitoring de drift Evidently pour CIF.

Definit les colonnes numeriques (les 25 features du modele) sur lesquelles
sont calculees les metriques de data drift et les seuils associes.

NOTE : les classes Evidently sont importees paresseusement (donnees de
reference) pour que ce module reste importable sans la bibliotheque Evidently
installee (la lib est une dependance optionnelle de l'environnement ML).
"""

from typing import Dict, List

# Les 25 features numeriques du modele (ordre du registre).
NUMERIC_FEATURES: List[str] = [
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

# Seuil de drift : proportion de colonnes declarees en drift.
DRIFT_THRESHOLD = 0.3

# Seuil K-S / PSI par colonne (defaut Evidently : 0.05).
COLUMN_DRIFT_THRESHOLD = 0.05


def get_data_quality_preset():
    """Rapport de qualite des donnees (DataQualityPreset Evidently)."""
    from evidently.metric_preset import DataQualityPreset

    return DataQualityPreset()


def get_data_drift_preset(columns: List[str] | None = None) -> dict:
    """Configuration du preset de data drift sur les features numeriques."""
    from evidently.metric_preset import DataDriftPreset

    preset = DataDriftPreset(num_stattest_threshold=COLUMN_DRIFT_THRESHOLD)
    # Evidently accepte une liste de colonnes numeriques ; on ne transmet
    # que la configuration textuelle pour compatibilite multi-versions.
    return {
        "preset": preset,
        "columns": columns or NUMERIC_FEATURES,
        "drift_share": DRIFT_THRESHOLD,
    }


def build_drift_report_config(columns: List[str] | None = None) -> Dict[str, float]:
    """Configuration JSON du monitoring (documentee / utilisee hors Evidently)."""
    return {
        "num_stattest_threshold": COLUMN_DRIFT_THRESHOLD,
        "drift_threshold": DRIFT_THRESHOLD,
        "n_features": len(columns or NUMERIC_FEATURES),
    }
