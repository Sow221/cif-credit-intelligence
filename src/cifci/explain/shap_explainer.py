"""Explicabilité du modèle via SHAP (transparence réglementaire).

Produit une explication locale par client (contribution de chaque feature
à la probabilité de défaut) et une importance globale agrégée.
"""

from __future__ import annotations

import pandas as pd
import shap


def explain_local(
    model,
    X: pd.DataFrame,
    *,
    background: pd.DataFrame | None = None,
    max_display: int = 30,
) -> pd.DataFrame:
    """Contributions SHAP locales de chaque feature pour chaque ligne de ``X``.

    Utilise ``TreeExplainer`` (adapté aux modèles XGBoost à base d'arbres).

    Returns:
        DataFrame (n_lignes × n_features) des valeurs SHAP. Les valeurs
        positives poussent vers le défaut (classe positive).
    """
    explainer = shap.TreeExplainer(model)
    matrix = X[list(model.feature_names_in_)] if hasattr(model, "feature_names_in_") else X
    shaps = explainer.shap_values(matrix)
    if isinstance(shaps, list):
        shaps = shaps[1]  # classe positive
    return pd.DataFrame(shaps, columns=matrix.columns)


def explain_one(
    model,
    X_row: pd.DataFrame,
    *,
    display_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Explication SHAP d'un seul client, triée par |contribution|.

    Returns:
        DataFrame avec ``feature`` et ``shap_value`` (ordonné desc).
    """
    cols = display_columns or (list(model.feature_names_in_) if hasattr(model, "feature_names_in_") else list(X_row.columns))
    if isinstance(X_row, pd.Series):
        X_row = X_row.to_frame().T
    X_row = X_row[cols]
    vals = explain_local(model, X_row).iloc[0]
    out = pd.DataFrame({"feature": vals.index, "shap_value": vals.values})
    return out.reindex(out["shap_value"].abs().sort_values(ascending=False).index).reset_index(drop=True)


def global_importance(
    model,
    X_ref: pd.DataFrame,
) -> pd.DataFrame:
    """Importance SHAP globale (moyenne des |valeurs|) sur ``X_ref``."""
    vals = explain_local(model, X_ref)
    mean_abs = vals.abs().mean(axis=0).sort_values(ascending=False)
    return pd.DataFrame({"feature": mean_abs.index, "mean_abs_shap": mean_abs.values})
