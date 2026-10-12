"""Tests des métriques du rapport de validation (KS, Gini, PSI)."""

import numpy as np

from avalix.evaluate.report import core_metrics, ks_stat, psi


def test_ks_perfect_and_random():
    y = np.array([0, 0, 0, 1, 1, 1])
    assert ks_stat(y, np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])) == 1.0
    rng = np.random.default_rng(0)
    yy = rng.integers(0, 2, 5000)
    assert ks_stat(yy, rng.random(5000)) < 0.06


def test_gini_is_two_auc_minus_one():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 2000)
    p = np.clip(y * 0.3 + rng.random(2000) * 0.7, 0, 1)
    m = core_metrics(y, p)
    assert abs(m["gini"] - (2 * m["roc_auc"] - 1)) < 1e-12


def test_psi_zero_on_same_distribution_and_large_on_shift():
    rng = np.random.default_rng(2)
    a = rng.normal(0, 1, 20000)
    assert psi(a, rng.normal(0, 1, 20000)) < 0.01
    assert psi(a, rng.normal(1.5, 1, 20000)) > 0.25
