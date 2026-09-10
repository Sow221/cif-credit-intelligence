from __future__ import annotations

from src.services.eligibility_service import EligibilityService


def test_eligible_application():
    service = EligibilityService()
    result = service.check({"requested_amount": 500000, "requested_term": 12})
    assert result.eligible is True
    assert len(result.reasons) == 0


def test_ineligible_low_amount():
    service = EligibilityService()
    result = service.check({"requested_amount": 5000, "requested_term": 12})
    assert result.eligible is False
    assert any("minimum" in r.lower() or "10,000" in r for r in result.reasons)


def test_ineligible_high_amount():
    service = EligibilityService()
    result = service.check({"requested_amount": 10000000, "requested_term": 12})
    assert result.eligible is False


def test_ineligible_invalid_term():
    service = EligibilityService()
    result = service.check({"requested_amount": 100000, "requested_term": 0})
    assert result.eligible is False
