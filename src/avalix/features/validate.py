"""Garde anti-leakage : valide qu'aucune variable interdite ou future
n'entre dans les features d'entraînement.

C'est un contrôle DÉFENSIF de la pipeline : si une variable qui encode la
cible (ex : ``p_default_true``) ou une variable post-décision réapparaît,
la validation échoue — la pipeline s'arrête avant tout entraînement.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class LeakageError(Exception):
    """Levée lorsqu'une variable interdite ou la cible est détectée."""


# Variables qui encodent directement la cible de défaut dans le générateur
# synthétique — interdites FORMELLEMENT dans toute feature d'entraînement.
# NB: `is_default` (la cible) n'est PAS listé ici ; elle se gère via
# `allow_target`. On interdit ici les variables de fuite "cachées".
FORBIDDEN_SUBSTRINGS: tuple[str, ...] = (
    "p_default",
    "probability_default",
    "true_default",
)


def forbidden_features(df: pd.DataFrame) -> list[str]:
    """Retourne la liste des colonnes de fuite présentes dans ``df``."""
    hits: list[str] = []
    for col in df.columns:
        lowered = str(col).lower()
        if any(tok in lowered for tok in FORBIDDEN_SUBSTRINGS):
            hits.append(str(col))
    return hits


def assert_no_leakage(
    df: pd.DataFrame,
    *,
    feature_columns: list[str] | None = None,
    allow_target: bool = True,
) -> pd.DataFrame:
    """Valide l'absence de fuite dans un DataFrame de features.

    Args:
        df: DataFrame à valider.
        feature_columns: liste attendue des features (hors cible). Si fournie,
            vérifie leur présence et rejette les colonnes inattendues.
        allow_target: si True, la colonne cible (``is_default``) est tolérée
            parmi les colonnes ; si False, elle est rejetée.

    Raises:
        LeakageError: si une variable de fuite est détectée, ou si les
            colonnes ne correspondent pas à la spécification.
    """
    hits = forbidden_features(df)
    if hits:
        raise LeakageError(
            "Variables de fuite (leakage potentiel) détectées dans les "
            f"features : {hits}. Supprimez-les avant tout entraînement."
        )

    if feature_columns is not None:
        missing = [c for c in feature_columns if c not in df.columns]
        if missing:
            raise LeakageError(
                f"Colonnes attendues absentes des features : {missing}."
            )
        allowed = set(feature_columns) | {
            "customer_id",
            "loan_id",
            "is_default" if allow_target else "",
        }
        extra = [c for c in df.columns if c not in allowed]
        if extra:
            raise LeakageError(
                f"Colonnes inattendues dans le jeu : {extra}."
            )

    return df


def load_and_validate(
    path: Path | str,
    *,
    feature_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Charge un CSV de features et le valide contre le leakage."""
    df = pd.read_csv(path)
    return assert_no_leakage(df, feature_columns=feature_columns)
