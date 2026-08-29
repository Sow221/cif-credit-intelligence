"""Tests anti-leakage.

Ces tests constituent la GARDE DÉFENSIVE de la pipeline : ils échouent si une
variable qui encode la cible (ex : ``p_default_true``) ou toute variable
post-décision réapparaît dans les features d'entraînement.

Le principe : un leak latent (présent dans ``features_prepared_*``) doit faire
rougir la CI afin que la correction soit OBLIGATOIRE avant tout déploiement.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cifci.config import PROJECT_ROOT, get_config
from cifci.features.validate import (
    LeakageError,
    assert_no_leakage,
    forbidden_features,
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def _discover_processed_csvs() -> list[Path]:
    if not PROCESSED_DIR.exists():
        return []
    return sorted(PROCESSED_DIR.glob("features_prepared_*.csv"))


def test_forbidden_substring_detects_p_default_true() -> None:
    """La logique de détection repère bien la variable qui encode la cible."""
    df = pd.DataFrame({"p_default_true": [0.1], "is_default": [1]})
    assert forbidden_features(df) == ["p_default_true"]


def test_assert_no_leakage_raises_on_forbidden() -> None:
    """assert_no_leakage doit lever une erreur en présence de leak."""
    df = pd.DataFrame({"age": [30], "p_default_true": [0.5]})
    with pytest.raises(LeakageError):
        assert_no_leakage(df, allow_target=False)


def test_assert_no_leakage_accepts_clean_features() -> None:
    """Un jeu de features saines passe sans erreur."""
    df = pd.DataFrame(
        {"age": [30], "monthly_income": [1_200_000.0], "is_default": [0]}
    )
    assert_no_leakage(df, allow_target=True)  # ne doit pas lever


def test_feature_columns_manifest_is_clean() -> None:
    """Le manifeste des features officielles ne contient aucun leak."""
    manifest = PROCESSED_DIR / "feature_columns.json"
    if not manifest.exists():
        pytest.skip("feature_columns.json absent")
    import json

    with manifest.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    feat = data["feature_columns"] + [data["target"]]
    assert forbidden_features(pd.DataFrame(columns=feat)) == [], (
        f"Le manifeste contient des variables interdites : "
        f"{forbidden_features(pd.DataFrame(columns=feat))}"
    )


@pytest.mark.parametrize("csv_path", _discover_processed_csvs(), ids=lambda p: p.name)
def test_processed_features_are_contamination_free(csv_path: Path) -> None:
    """AUCUN fichier de features préparées ne doit contenir de leak latent.

    ⚠️ Si ce test échoue, il signale un leak résiduel NON purgé dans
    ``data/processed/``. C'est un blocage volontaire : toute feature issue
    de ce fichier serait disqualifiante pour un audit CIF.
    """
    df = pd.read_csv(csv_path)
    assert forbidden_features(df) == [], (
        f"FICHIER CONTAMINÉ : {csv_path.name} contient des variables "
        f"interdites : {forbidden_features(df)}. "
        "Le leak est NON purgé — corrigez le feature engineering."
    )


def test_params_features_are_allowed() -> None:
    """Les features déclarées dans params.yaml sont toutes autorisées."""
    cfg = get_config()
    feat = cfg.features.get("list", [])
    forbidden = cfg.features.get("forbidden_variables", [])
    assert forbidden_features(pd.DataFrame(columns=[*feat, *forbidden])) == [
        *forbidden
    ], "Les variables interdites ne sont pas toutes purgées de la liste features."
    # Aucune feature autorisée ne doit être interdite
    flagged = forbidden_features(pd.DataFrame(columns=feat))
    assert flagged == [], f"params.yaml contient des features interdites : {flagged}"
