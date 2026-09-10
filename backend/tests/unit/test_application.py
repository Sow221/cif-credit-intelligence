from __future__ import annotations

from src.schemas.application import CreateApplicationRequest
from src.services.application_service import VALID_TRANSITIONS


def test_application_schema():
    data = CreateApplicationRequest(
        client_id=__import__("uuid").uuid4(),
        product_id="MICRO_CREDIT",
        requested_amount=500000,
        requested_term=12,
    )
    assert data.requested_amount == 500000


def test_valid_transitions():
    assert "SUBMITTED" in VALID_TRANSITIONS["DRAFT"]
    assert "CANCELLED" in VALID_TRANSITIONS["DRAFT"]
    assert "DATA_VALIDATION" in VALID_TRANSITIONS["SUBMITTED"]
