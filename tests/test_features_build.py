"""Tests de la construction des 25 features officielles.

Vérifie que ``build_features`` reproduit exactement le contrat du modèle
officiel : 25 colonnes, sans aucune variable de fuite, cible conservée.
"""

from __future__ import annotations

import pandas as pd
import pytest

from cifci.config import get_config
from cifci.data.ingest import load_customers, load_loans
from cifci.features.build import build_features, prepare_feature_matrix
from cifci.features.validate import LeakageError


@pytest.fixture(scope="module")
def real_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    return load_customers(), load_loans()


def test_build_features_matches_official_schema(real_data) -> None:
    cust, loans = real_data
    df = build_features(cust, loans)
    officials = set(get_config().features["list"])
    assert officials <= set(df.columns)
    extra = set(df.columns) - officials - {"customer_id", "is_default"}
    assert extra == set()


def test_build_features_is_clean_of_leak(real_data) -> None:
    cust, loans = real_data
    df = build_features(cust, loans)
    assert "p_default_true" not in df.columns
    low = {c.lower() for c in df.columns}
    assert not any("p_default" in c for c in low)


def test_target_is_kept(real_data) -> None:
    cust, loans = real_data
    df = build_features(cust, loans)
    assert "is_default" in df.columns


def test_prepare_feature_matrix_shapes(real_data) -> None:
    cust, loans = real_data
    X, y = prepare_feature_matrix(cust, loans)  # noqa: N806
    n_feat = len(get_config().features["list"])
    assert X.shape[1] == n_feat
    assert y is not None
    assert len(X) == len(y)


def test_prepare_feature_matrix_drop_target(real_data) -> None:
    cust, loans = real_data
    X, y = prepare_feature_matrix(cust, loans, drop_target=True)  # noqa: N806
    assert y is None
    assert "is_default" not in X.columns


def test_aggregate_loans_thin_file_zero(real_data) -> None:
    cust, loans = real_data
    df = build_features(cust, loans)
    # Un client sans historique n'apparaît pas dans l'agrégation (join left).
    thin = df[df["n_loans"] == 0]
    assert (thin["total_loan_amount"] == 0).all()


def test_leakage_error_raised_on_contaminated() -> None:
    cust, loans = load_customers(), load_loans()
    if "p_default_true" in cust.columns:
        with pytest.raises(LeakageError):
            # En désactivant la suppression, la garde doit lever.
            build_features(cust, loans, drop_forbidden=False)
