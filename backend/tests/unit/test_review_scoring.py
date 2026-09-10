from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch


def _mock_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.query = MagicMock()
    return db


# --- Review Service full coverage ---
def test_review_assign_success():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    mock_review = MagicMock()
    mock_review.review_id = uuid.uuid4()
    mock_review.status = "PENDING"
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_review
        result = svc.assign(uuid.uuid4(), uuid.uuid4())
        assert result.status == "ASSIGNED"


def test_review_assign_not_found():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        try:
            svc.assign(uuid.uuid4(), uuid.uuid4())
            assert False, "Should raise"
        except Exception:
            pass


def test_review_assign_invalid_transition():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    mock_review = MagicMock()
    mock_review.review_id = uuid.uuid4()
    mock_review.status = "COMPLETED"
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_review
        try:
            svc.assign(uuid.uuid4(), uuid.uuid4())
            assert False, "Should raise"
        except Exception:
            pass


def test_review_start_success():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    mock_review = MagicMock()
    mock_review.review_id = uuid.uuid4()
    mock_review.status = "ASSIGNED"
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_review
        result = svc.start(uuid.uuid4())
        assert result.status == "IN_PROGRESS"


def test_review_start_not_found():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        try:
            svc.start(uuid.uuid4())
            assert False, "Should raise"
        except Exception:
            pass


def test_review_start_invalid_transition():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    mock_review = MagicMock()
    mock_review.review_id = uuid.uuid4()
    mock_review.status = "PENDING"
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_review
        try:
            svc.start(uuid.uuid4())
            assert False, "Should raise"
        except Exception:
            pass


def test_review_complete_success():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    mock_review = MagicMock()
    mock_review.review_id = uuid.uuid4()
    mock_review.status = "IN_PROGRESS"
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_review
        result = svc.complete(uuid.uuid4(), "APPROVE")
        assert result.status == "COMPLETED"
        assert result.final_action == "APPROVE"


def test_review_complete_not_found():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        try:
            svc.complete(uuid.uuid4(), "APPROVE")
            assert False, "Should raise"
        except Exception:
            pass


def test_review_complete_invalid_transition():
    from src.services.review_service import ReviewService

    db = _mock_db()
    svc = ReviewService(db)
    mock_review = MagicMock()
    mock_review.review_id = uuid.uuid4()
    mock_review.status = "PENDING"
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_review
        try:
            svc.complete(uuid.uuid4(), "APPROVE")
            assert False, "Should raise"
        except Exception:
            pass


# --- Scoring Service ---
def test_scoring_service_score_no_model():
    from src.core.exceptions import ModelNotAvailableError
    from src.services.scoring_service import ScoringService

    db = _mock_db()
    svc = ScoringService(db)
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        try:
            svc.score(uuid.uuid4(), uuid.uuid4(), {"monthly_income": 500000})
            assert False, "Should raise ModelNotAvailableError"
        except ModelNotAvailableError:
            pass


def test_scoring_service_score_with_production_model():
    from src.services.scoring_service import ScoringService

    db = _mock_db()
    svc = ScoringService(db)
    mock_model = MagicMock()
    mock_model.status = "PRODUCTION"
    mock_model.version = "v1.0"
    mock_model.model_version_id = uuid.uuid4()
    with patch.object(svc.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_model
        with patch.object(svc.risk_engine, "score", return_value=0.3):
            with patch.object(svc.db, "add"):
                with patch.object(svc.db, "commit"):
                    with patch.object(
                        svc.db,
                        "refresh",
                        side_effect=lambda x: setattr(x, "prediction_id", uuid.uuid4()),
                    ):
                        result = svc.score(
                            uuid.uuid4(),
                            uuid.uuid4(),
                            {"monthly_income": 500000, "debt_to_income": 0.2},
                        )
                        assert "prediction_id" in result
                        assert "pd_raw" in result
                        assert "uncertainty" in result
