"""Construction des 25 features officielles du modèle CIF.

Reconstruit le pipeline de feature engineering qui transforme les tables
brutes ``customers`` + ``loans`` en la matrice de 25 features utilisée par
``MODEL_OFFICIAL_CALIBRATED.joblib`` (liste exacte dans
``configs/params.yaml``).

La fusion applique la garde anti-leakage : ``p_default_true`` et toute
variable de fuite sont FORMELLEMENT exclues (voir ``features.validate``).
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from cifci.config import get_config
from cifci.features.validate import LeakageError, assert_no_leakage, forbidden_features

# Colonnes de la table customers que l'on conserve (id + cible gérés à part)
_CUSTOMER_FEATURE_COLS = [
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
]


def aggregate_loans(loans: pd.DataFrame) -> pd.DataFrame:
    """Agrège l'historique de prêts par client en features numériques.

    Groupe ``loans`` sur ``customer_id`` et calcule les statistiques
    utilisées par le modèle officiel (montants, régularité, DPD, défauts).
    """
    loans = loans.copy()
    agg = (
        loans.groupby("customer_id")
        .agg(
            n_loans=("loan_amount", "size"),
            avg_loan_amount=("loan_amount", "mean"),
            total_loan_amount=("loan_amount", "sum"),
            avg_repayment_regularity=("repayment_regularity", "mean"),
            min_repayment_regularity=("repayment_regularity", "min"),
            max_historical_dpd=("max_dpd", "max"),
            mean_historical_dpd=("max_dpd", "mean"),
            n_defaults=("loan_status", lambda s: int((s == "default").sum())),
        )
        .reset_index()
    )
    # Ratio historique de défaut (évite la division par zéro)
    agg["historical_default_rate"] = agg["n_defaults"] / np.maximum(
        agg["n_loans"], 1
    )
    return agg


def build_features(
    customers: pd.DataFrame,
    loans: pd.DataFrame,
    *,
    drop_forbidden: bool = True,
) -> pd.DataFrame:
    """Construit la matrice de features (25 colonnes) pour le modèle officiel.

    Args:
        customers: table clients brute (avec ``customer_id``, ``is_default``).
        loans: historique de prêts à agréger par client.
        drop_forbidden: si True (recommandé), supprime les variables de fuite
            présentes en entrée (``p_default_true``...). La cible ``is_default``
            est conservée pour l'entraînement.

    Returns:
        DataFrame de features avec au minimum les 25 colonnes officielles
        plus ``customer_id`` et ``is_default``.
    """
    cfg = get_config()
    feature_columns = list(cfg.features["list"])

    if drop_forbidden:
        hits = forbidden_features(customers)
        if hits:
            warnings.warn(
                f"Variables de fuite détectées et supprimées : {hits}.",
                stacklevel=2,
            )
            customers = customers.drop(columns=[c for c in hits if c in customers])
    else:
        # Mode défensif strict : on refuse d'avancer tant que la donnée
        # d'entrée contient une variable de fuite.
        hits = forbidden_features(customers)
        if hits:
            raise LeakageError(
                "drop_forbidden=False et variables de fuite détectées en "
                f"entrée : {hits}. Corrigez la donnée avant l'entraînement."
            )

    loan_agg = aggregate_loans(loans)
    merged = customers.merge(loan_agg, on="customer_id", how="left")

    # Remplit les clients sans historique de prêt (thin-file) par des neutres
    for col in [
        "n_loans",
        "avg_loan_amount",
        "total_loan_amount",
        "avg_repayment_regularity",
        "min_repayment_regularity",
        "max_historical_dpd",
        "mean_historical_dpd",
        "n_defaults",
        "historical_default_rate",
    ]:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)

    # Features dérivées (rapports et conversions d'unités)
    merged["loan_to_income_ratio"] = (
        merged["current_loan_request"] / merged["monthly_income"].replace(0, np.nan)
    )
    merged["savings_to_income_ratio"] = (
        merged["current_savings"] / merged["monthly_income"].replace(0, np.nan)
    )
    merged["seniority_years"] = merged["seniority_months"] / 12.0
    merged["overall_payment_regularity"] = merged["avg_repayment_regularity"]

    # Colonnes de sortie : features officielles + clés/cible
    out_cols = ["customer_id", *feature_columns]
    if "is_default" in merged.columns:
        out_cols.append("is_default")
    result = merged[out_cols].copy()

    # Garde anti-leakage : s'assure que la sortie est propre et complète.
    return assert_no_leakage(
        result, feature_columns=feature_columns, allow_target=True
    )


def prepare_feature_matrix(
    customers: pd.DataFrame,
    loans: pd.DataFrame,
    *,
    drop_target: bool = False,
) -> tuple[pd.DataFrame, pd.Series | None]:
    """Prépare (X, y) prêts pour l'entraînement.

    Returns:
        (X, y) où X contient uniquement les 25 features (sans id ni cible)
        et y la série cible (None si ``drop_target``).
    """
    df = build_features(customers, loans)
    feature_columns = list(get_config().features["list"])
    X = df[feature_columns].copy()  # noqa: N806 (convention ML)
    y = df["is_default"] if "is_default" in df.columns else None
    if drop_target:
        y = None
    return X, y
