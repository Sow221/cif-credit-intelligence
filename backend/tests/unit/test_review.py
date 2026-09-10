from __future__ import annotations

from src.schemas.review import AssignReviewRequest, CompleteReviewRequest, ReviewResponse


def test_review_response():
    r = ReviewResponse(
        review_id="123", application_id="456", status="PENDING", review_reason="High uncertainty"
    )
    assert r.status == "PENDING"


def test_assign_request():
    import uuid

    req = AssignReviewRequest(assigned_to=uuid.uuid4())
    assert req.assigned_to is not None


def test_complete_request():
    req = CompleteReviewRequest(final_action="APPROVE")
    assert req.final_action == "APPROVE"
