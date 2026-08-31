"""Tests unitaires du module de qualite des donnees (P0, etape 5 / 8)."""

from datetime import datetime

import pytest

from src.core.exceptions import DataQualityError, TemporalGuardError
from src.features.data_quality import (
    DataQualityChecker,
    DataQualityConfig,
    DataQualityField,
    DataQualityStatus,
    DataSourceStatus,
)


def _field(name="income", value=1000.0, observed_at=None, source=None):
    return DataQualityField(
        field_name=name,
        field_value=value,
        observed_at=observed_at,
        source=source or DataSourceStatus(code="BANK", active=True),
    )


def test_pass_no_issues():
    result = DataQualityChecker().evaluate([_field()])
    assert result.status == DataQualityStatus.PASS
    assert result.data_ready_for_auto_scoring is True


def test_fail_when_source_inactive():
    field = _field(source=DataSourceStatus(code="BANK", active=False))
    result = DataQualityChecker().evaluate([field])
    assert result.status == DataQualityStatus.FAIL
    assert result.data_ready_for_auto_scoring is False
    assert result.checks["source_status"] == DataQualityStatus.FAIL


def test_warning_when_field_missing():
    field = _field(value=None)
    result = DataQualityChecker().evaluate([field])
    assert result.status == DataQualityStatus.WARNING
    assert result.data_ready_for_auto_scoring is True


def test_fail_when_invalid_range():
    config = DataQualityConfig(valid_ranges={"income": (0.0, 1_000_000.0)})
    result = DataQualityChecker(config).evaluate([_field(value=5_000_000.0)])
    assert result.status == DataQualityStatus.FAIL
    assert result.checks["validity"] == DataQualityStatus.FAIL


def test_fail_when_schema_type_mismatch():
    config = DataQualityConfig(expected_types={"income": "float"})
    result = DataQualityChecker(config).evaluate([_field(value="abc")])
    assert result.status == DataQualityStatus.FAIL
    assert result.checks["schema"] == DataQualityStatus.FAIL


def test_temporal_guard_rejects_future_data():
    config = DataQualityConfig(application_timestamp=datetime(2026, 1, 1))
    field = _field(observed_at=datetime(2026, 6, 1))
    result = DataQualityChecker(config).evaluate([field])
    assert result.status == DataQualityStatus.FAIL
    assert result.rejected_fields == ["income"]
    assert result.checks["temporal_validity"] == DataQualityStatus.FAIL


def test_temporal_ok_when_observed_before_application():
    config = DataQualityConfig(application_timestamp=datetime(2026, 6, 1))
    field = _field(observed_at=datetime(2026, 1, 1))
    result = DataQualityChecker(config).evaluate([field])
    assert result.status == DataQualityStatus.PASS
    assert result.rejected_fields == []


def test_assert_scoreable_raises_on_fail():
    field = _field(source=DataSourceStatus(code="BANK", active=False))
    result = DataQualityChecker().evaluate([field])
    with pytest.raises(DataQualityError):
        DataQualityChecker().assert_scoreable(result)


def test_assert_temporal_raises_on_rejected():
    config = DataQualityConfig(application_timestamp=datetime(2026, 1, 1))
    field = _field(observed_at=datetime(2026, 6, 1))
    result = DataQualityChecker(config).evaluate([field])
    with pytest.raises(TemporalGuardError):
        DataQualityChecker(config).assert_temporal(result)
