"""Fixtures communes : amorce données synthétiques et modèle si absents.

Sans ce fichier, les tests dépendaient de CSV et d'un modèle suivis par DVC,
absents d'un clone frais (et donc de la CI).
"""

from __future__ import annotations

import warnings

import pytest


@pytest.fixture(scope="session", autouse=True)
def _bootstrap_artifacts() -> None:
    from avalix.data.bootstrap import ensure_model, ensure_raw_data

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ensure_raw_data()
        ensure_model()
