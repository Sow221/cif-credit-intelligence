"""Tests du feature engine (P0, etape 9).

Couvre le registre des definitions (25 features APPROVED), le catalogue des
sets versionnes (MINIMAL..FULL_ADMISSIBLE) et la resolution du set selon le
profil d'information. Composant pur : aucun acces DB necessaire.
"""

from src.features.feature_engine import (
    DEFAULT_CATALOG,
    FeatureStatus,
    build_feature_definitions,
    resolve_feature_set,
)
from src.features.information_profiler import InformationState


def test_registry_has_25_approved_features() -> None:
    definitions = build_feature_definitions()
    assert len(definitions) == 25
    assert all(d.status == FeatureStatus.APPROVED for d in definitions)
    names = {d.name for d in definitions}
    assert "monthly_income" in names
    assert "max_historical_dpd" in names


def test_catalog_has_six_versioned_sets() -> None:
    codes = DEFAULT_CATALOG.list_codes()
    assert set(codes) == {
        "MINIMAL", "BUSINESS", "FINANCIAL", "CREDIT", "ALTERNATIVE", "FULL_ADMISSIBLE",
    }
    for code in codes:
        feature_set = DEFAULT_CATALOG.get(code, "1")
        assert feature_set is not None
        assert feature_set.version == "1"
        assert len(feature_set.features) > 0


def test_versions_are_unique_identifiers() -> None:
    # Chaque set reference bien sa version ; un set inconnu rend None.
    assert DEFAULT_CATALOG.get("MINIMAL", "1") is not None
    assert DEFAULT_CATALOG.get("MINIMAL", "999") is None
    assert DEFAULT_CATALOG.get("INEXISTANT", "1") is None


def test_minimal_set_is_contained_in_full() -> None:
    minimal = set(DEFAULT_CATALOG.get("MINIMAL", "1").features)
    full = set(DEFAULT_CATALOG.get("FULL_ADMISSIBLE", "1").features)
    assert minimal.issubset(full)
    assert len(minimal) == 5


def test_resolve_uses_information_state_only() -> None:
    # La resolution est deterministe et ne depend que du profil d'information.
    assert resolve_feature_set(InformationState.FULL_FILE).code == "FULL_ADMISSIBLE"
    assert resolve_feature_set(InformationState.THIN_FILE).code == "FINANCIAL"
    assert resolve_feature_set(InformationState.NO_FILE).code == "MINIMAL"
    assert resolve_feature_set(None).code == "MINIMAL"
