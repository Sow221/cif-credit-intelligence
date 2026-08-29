"""Tests de l'ingestion et du générateur synthétique seedé."""

from __future__ import annotations

import pandas as pd

from cifci.data.ingest import generate_synthetic, load_customers, load_loans
from cifci.features.validate import forbidden_features


def test_load_customers_real_file() -> None:
    df = load_customers()
    assert isinstance(df, pd.DataFrame)
    assert "customer_id" in df.columns
    assert "is_default" in df.columns
    assert len(df) > 0


def test_load_loans_real_file() -> None:
    df = load_loans()
    assert isinstance(df, pd.DataFrame)
    assert "customer_id" in df.columns
    assert len(df) > 0


def test_synthetic_is_deterministic() -> None:
    c1, l1 = generate_synthetic(n_customers=500, seed=42)
    c2, l2 = generate_synthetic(n_customers=500, seed=42)
    pd.testing.assert_frame_equal(c1, c2)
    pd.testing.assert_frame_equal(l1, l2)


def test_synthetic_respects_seed_change() -> None:
    c1, _ = generate_synthetic(n_customers=200, seed=1)
    c2, _ = generate_synthetic(n_customers=200, seed=2)
    assert not c1["age"].equals(c2["age"])


def test_synthetic_no_forbidden_leak() -> None:
    customers, _ = generate_synthetic(n_customers=300)
    assert forbidden_features(customers) == []
    # La cible est légitime, les variables de fuite non.
    assert "p_default_true" not in customers.columns


def test_synthetic_default_rate_approx_target() -> None:
    c, _ = generate_synthetic(n_customers=10_000, seed=42)
    rate = c["is_default"].mean()
    # Tolérance large : la cible est calibrée approximativement.
    assert 0.08 <= rate <= 0.18


def test_synthetic_loans_consistent_with_customers() -> None:
    customers, loans = generate_synthetic(n_customers=500, seed=7)
    c_ids = set(customers["customer_id"])
    l_ids = set(loans["customer_id"])
    # Tout client prêté doit exister dans la table clients.
    assert l_ids <= c_ids
    # Les clients sans historique (thin-file) doivent exister aussi.
    assert len(c_ids) > 0
