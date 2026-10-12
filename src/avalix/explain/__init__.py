"""Explicabilité du modèle (SHAP, local et global)."""

from avalix.explain.shap_explainer import (
    explain_local,
    explain_one,
    global_importance,
)

__all__ = ["explain_local", "explain_one", "global_importance"]
