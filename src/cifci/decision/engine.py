"""Moteur de décision CIF : probabilité calibrée → décision métier.

Convertit la probabilité de défaut calibrée d'un client en une décision
parmi APPROBATION / REVUE_HUMAINE / AJUSTEMENT / REFUS, selon les seuils
et hypothèses de coût déclarés dans ``configs/params.yaml``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from cifci.config import get_config

# Décisions possibles (ordre croissant de risque).
DECISIONS = ["APPROBATION", "REVUE_HUMAINE", "AJUSTEMENT", "REFUS"]


def decision_for_probability(p: float) -> str:
    """Transforme une probabilité de défaut en décision métier.

    Seuils (config): auto_approve → APPROBATION ; human_review → REVUE ;
    adjust → AJUSTEMENT ; au-delà de hard_refuse → REFUS.
    """
    cfg = get_config()
    t = cfg.decision_engine["thresholds"]
    if p < t["auto_approve"]:
        return "APPROBATION"
    if p < t["human_review"]:
        return "REVUE_HUMAINE"
    if p < t["adjust"]:
        return "AJUSTEMENT"
    return "REFUS"


def decide(
    prob: pd.Series | np.ndarray | list[float],
    *,
    history_len: pd.Series | np.ndarray | list[int] | None = None,
) -> pd.DataFrame:
    """Applique le moteur de décision sur un vecteur de probabilités.

    Args:
        prob: probabilités de défaut calibrées.
        history_len: facultatif, nombre de prêts passés (thin-file boost).

    Returns:
        DataFrame avec colonnes ``prob``, ``history_len``, ``decision``.
    """
    p = np.asarray(prob, dtype=float)
    n = len(p)
    has_history = history_len is not None
    if has_history:
        hist = pd.Series(np.asarray(history_len, dtype=float))
    else:
        hist = pd.Series([1] * n, dtype=float)

    decisions = []
    thin_boost = bool(get_config().decision_engine.get("thin_file_boost_review", True))
    for i in range(n):
        d = decision_for_probability(p[i])
        # Les thin-file (sans historique, connu = 0) sont orientés revue humaine.
        # NB: si l'historique est inconnu (None), on n'applique pas ce boost.
        if thin_boost and has_history and hist.iloc[i] == 0 and d == "APPROBATION":
            d = "REVUE_HUMAINE"
        decisions.append(d)

    return pd.DataFrame(
        {"prob": p, "history_len": hist.to_numpy(), "decision": decisions}
    )


def decision_distribution(decisions: pd.DataFrame) -> dict[str, int]:
    """Retourne la répartition des décisions (conte / ratio)."""
    vc = decisions["decision"].value_counts()
    return {d: int(vc.get(d, 0)) for d in DECISIONS}
