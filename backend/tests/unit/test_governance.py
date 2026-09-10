from __future__ import annotations

from unittest.mock import MagicMock

from src.governance.consent import ConsentService
from src.governance.lineage import LineageService


def test_consent_service_init():
    mock_db = MagicMock()
    service = ConsentService(mock_db)
    assert service.VALID_STATUSES == {"GRANTED", "REFUSED", "REVOKED", "NOT_REQUIRED", "UNKNOWN"}


def test_lineage_service_init():
    mock_db = MagicMock()
    service = LineageService(mock_db)
    assert service is not None
