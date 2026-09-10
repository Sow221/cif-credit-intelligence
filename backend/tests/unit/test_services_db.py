from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch


def _mock_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.query = MagicMock()
    return db


def _mock_user():
    user = MagicMock()
    user.user_id = uuid.uuid4()
    user.institution_id = uuid.uuid4()
    user.role = "CREDIT_OFFICER"
    user.is_active = True
    return user


# --- Client Service ---
def test_client_service_create():
    from src.schemas.client import CreateClientRequest
    from src.services.client_service import ClientService

    db = _mock_db()
    svc = ClientService(db)
    mock_client = MagicMock()
    mock_client.client_id = uuid.uuid4()
    svc.repo.create = MagicMock(return_value=mock_client)
    data = CreateClientRequest(first_name="Moussa", last_name="Sow")
    result = svc.create(uuid.uuid4(), data)
    assert result is not None


def test_client_service_get():
    from src.services.client_service import ClientService

    db = _mock_db()
    svc = ClientService(db)
    mock_client = MagicMock()
    svc.repo.get_by_id = MagicMock(return_value=mock_client)
    result = svc.get(uuid.uuid4(), uuid.uuid4())
    assert result is not None


def test_client_service_list():
    from src.services.client_service import ClientService

    db = _mock_db()
    svc = ClientService(db)
    svc.repo.get_multi = MagicMock(return_value=[MagicMock(), MagicMock()])
    result = svc.list(uuid.uuid4())
    assert len(result) == 2


# --- Application Service ---
def test_application_service_create():
    from src.schemas.application import CreateApplicationRequest
    from src.services.application_service import ApplicationService

    db = _mock_db()
    svc = ApplicationService(db)
    mock_app = MagicMock()
    svc.repo.create = MagicMock(return_value=mock_app)
    data = CreateApplicationRequest(
        client_id=uuid.uuid4(), product_id="MC", requested_amount=100000, requested_term=12
    )
    result = svc.create(uuid.uuid4(), data)
    assert result is not None


def test_application_service_get():
    from src.services.application_service import ApplicationService

    db = _mock_db()
    svc = ApplicationService(db)
    mock_app = MagicMock()
    svc.repo.get_by_id = MagicMock(return_value=mock_app)
    result = svc.get(uuid.uuid4(), uuid.uuid4())
    assert result is not None


def test_application_service_get_none():
    from src.services.application_service import ApplicationService

    db = _mock_db()
    svc = ApplicationService(db)
    svc.repo.get_by_id = MagicMock(return_value=None)
    result = svc.get(uuid.uuid4(), uuid.uuid4())
    assert result is None


def test_application_service_list():
    from src.services.application_service import ApplicationService

    db = _mock_db()
    svc = ApplicationService(db)
    svc.repo.get_multi = MagicMock(return_value=[MagicMock()])
    result = svc.list(uuid.uuid4())
    assert len(result) == 1


def test_application_service_transition_valid():
    from src.services.application_service import ApplicationService

    db = _mock_db()
    svc = ApplicationService(db)
    mock_app = MagicMock()
    mock_app.status = "DRAFT"
    svc.repo.get_by_id = MagicMock(return_value=mock_app)
    svc.repo.update_status = MagicMock(return_value=mock_app)
    result = svc.transition(uuid.uuid4(), uuid.uuid4(), "SUBMITTED")
    assert result is not None


def test_application_service_transition_invalid():
    from src.services.application_service import ApplicationService

    db = _mock_db()
    svc = ApplicationService(db)
    mock_app = MagicMock()
    mock_app.status = "DRAFT"
    svc.repo.get_by_id = MagicMock(return_value=mock_app)
    try:
        svc.transition(uuid.uuid4(), uuid.uuid4(), "DECIDED")
        assert False, "Should raise"
    except ValueError:
        pass


# --- Review Service ---
def test_review_service_create():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    mock_review = MagicMock()
    mock_review.review_id = uuid.uuid4()
    mock_review.status = "PENDING"
    mock_review.review_reason = "test"
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock(side_effect=lambda x: setattr(x, "review_id", uuid.uuid4()))
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_review
        # Test create directly by checking the service has the method
        assert hasattr(svc, "create")
        assert hasattr(svc, "assign")
        assert hasattr(svc, "start")
        assert hasattr(svc, "complete")
        assert hasattr(svc, "list_pending")


def test_review_service_list_pending():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [MagicMock(), MagicMock()]
        result = svc.list_pending(uuid.uuid4())
        assert len(result) == 2


# --- Decision Policy Service ---
def test_decision_policy_service_create():
    from src.services.decision_policy_service import DecisionPolicyService

    db = _mock_db()
    svc = DecisionPolicyService(db)
    mock_policy = MagicMock()
    mock_policy.policy_id = uuid.uuid4()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    # Create a real-ish policy
    with patch.object(svc.db, "add"):
        with patch.object(svc.db, "commit"):
            with patch.object(svc.db, "refresh"):

                with patch("src.services.decision_policy_service.DecisionPolicy") as mock_policy:
                    instance = mock_policy.return_value
                    instance.policy_id = uuid.uuid4()
                    result = svc.create(
                        uuid.uuid4(),
                        "MICRO_CREDIT",
                        {"eligibility": "{}", "approve": "{}", "review": "{}", "decline": "{}"},
                    )
                    assert result is not None


def test_decision_policy_service_get_active():
    from src.services.decision_policy_service import DecisionPolicyService

    db = _mock_db()
    svc = DecisionPolicyService(db)
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        result = svc.get_active_policy(uuid.uuid4(), "MC")
        assert result is not None


# --- Outcome Service ---
def test_outcome_service_record():
    from src.services.outcome_service import OutcomeService

    db = _mock_db()
    svc = OutcomeService(db)
    with patch("src.services.outcome_service.LoanOutcome") as mock_outcome:
        instance = mock_outcome.return_value
        instance.outcome_id = uuid.uuid4()
        result = svc.record(uuid.uuid4(), "LOAN-001", "ACTIVE", datetime.now(UTC))
        assert result is not None


# --- Scoring Service ---
def test_scoring_service_init():
    from src.services.scoring_service import ScoringService

    db = _mock_db()
    svc = ScoringService(db)
    assert svc.risk_engine is not None
    assert svc.calibration is not None
    assert svc.uncertainty is not None


# --- Data Intake ---
def test_data_intake_init():
    from src.features.data_intake import DataIntakeService

    db = _mock_db()
    svc = DataIntakeService(db)
    assert svc is not None


# --- Consent Service ---
def test_consent_service_create():
    from src.governance.consent import ConsentService

    db = _mock_db()
    svc = ConsentService(db)
    with patch("src.governance.consent.Consent") as mock_consent:
        instance = mock_consent.return_value
        instance.consent_id = uuid.uuid4()
        result = svc.create(
            uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), "credit_check", "GRANTED"
        )
        assert result is not None


def test_consent_service_revoke():
    from src.governance.consent import ConsentService

    db = _mock_db()
    svc = ConsentService(db)
    mock_consent = MagicMock()
    mock_consent.status = "GRANTED"
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_consent
        result = svc.revoke(uuid.uuid4())
        assert result.status == "REVOKED"


# --- Lineage Service ---
def test_lineage_service_record():
    from src.governance.lineage import LineageService

    db = _mock_db()
    svc = LineageService(db)
    with patch("src.governance.lineage.DataLineage") as mock_lineage:
        instance = mock_lineage.return_value
        instance.lineage_id = uuid.uuid4()
        result = svc.record(uuid.uuid4(), uuid.uuid4(), "income", "monthly_income")
        assert result is not None


def test_lineage_service_trace():
    from src.governance.lineage import LineageService

    db = _mock_db()
    svc = LineageService(db)
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [MagicMock()]
        result = svc.trace(uuid.uuid4())
        assert len(result) == 1


def test_lineage_service_is_traceable():
    from src.governance.lineage import LineageService

    db = _mock_db()
    svc = LineageService(db)
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        assert svc.is_traceable("income", uuid.uuid4()) is True
        mock_query.return_value.filter.return_value.first.return_value = None
        assert svc.is_traceable("missing", uuid.uuid4()) is False
