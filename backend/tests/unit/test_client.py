from __future__ import annotations

from unittest.mock import MagicMock

from src.schemas.client import CreateClientRequest
from src.services.client_service import ClientService


def test_create_client_schema():
    data = CreateClientRequest(first_name="Moussa", last_name="Sow", phone="+221770000000")
    assert data.first_name == "Moussa"
    assert data.last_name == "Sow"


def test_create_client_service():
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    service = ClientService(mock_db)
    assert service is not None
