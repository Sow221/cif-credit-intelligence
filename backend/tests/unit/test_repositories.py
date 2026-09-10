from __future__ import annotations

from unittest.mock import MagicMock

from src.repositories.application_repository import ApplicationRepository
from src.repositories.audit_repository import AuditRepository
from src.repositories.client_repository import ClientRepository
from src.repositories.review_repository import ReviewRepository


def test_client_repo_init():
    mock_db = MagicMock()
    repo = ClientRepository(mock_db)
    assert repo is not None


def test_application_repo_init():
    mock_db = MagicMock()
    repo = ApplicationRepository(mock_db)
    assert repo is not None


def test_audit_repo_init():
    mock_db = MagicMock()
    repo = AuditRepository(mock_db)
    assert repo is not None


def test_review_repo_init():
    mock_db = MagicMock()
    repo = ReviewRepository(mock_db)
    assert repo is not None
