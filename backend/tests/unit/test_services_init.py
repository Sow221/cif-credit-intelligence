from __future__ import annotations

from unittest.mock import MagicMock

from src.services.application_service import ApplicationService
from src.services.client_service import ClientService
from src.services.decision_policy_service import DecisionPolicyService
from src.services.eligibility_service import EligibilityService
from src.services.outcome_service import OutcomeService
from src.services.review_service import ReviewService
from src.services.scoring_service import ScoringService


def test_client_service_init():
    mock_db = MagicMock()
    svc = ClientService(mock_db)
    assert svc is not None


def test_application_service_init():
    mock_db = MagicMock()
    svc = ApplicationService(mock_db)
    assert svc is not None


def test_eligibility_service_init():
    svc = EligibilityService()
    assert len(svc.rules) > 0


def test_decision_policy_service_init():
    mock_db = MagicMock()
    svc = DecisionPolicyService(mock_db)
    assert svc is not None


def test_review_service_init():
    mock_db = MagicMock()
    svc = ReviewService(mock_db)
    assert svc is not None


def test_outcome_service_init():
    mock_db = MagicMock()
    svc = OutcomeService(mock_db)
    assert svc is not None


def test_scoring_service_init():
    mock_db = MagicMock()
    svc = ScoringService(mock_db)
    assert svc is not None
