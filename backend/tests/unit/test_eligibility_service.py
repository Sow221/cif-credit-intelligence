"""Tests unitaires du service d'eligibilite (P0, etape 4)."""

import pytest

from src.schemas.eligibility import (
    EligibilityInput,
    EligibilityRules,
    EligibilityStatus,
)
from src.services.eligibility_service import EligibilityService


def test_eligible_with_default_rules():
    result = EligibilityService().evaluate(
        EligibilityInput(client_age=30, requested_amount=500000.0, requested_term=12)
    )
    assert result.status == EligibilityStatus.ELIGIBLE
    assert result.eligible is True
    assert result.reasons == []
    assert result.rules_version == "1.0"


def test_not_eligible_under_minimum_age():
    result = EligibilityService().evaluate(
        EligibilityInput(client_age=17, requested_amount=1000.0, requested_term=12)
    )
    assert result.status == EligibilityStatus.NOT_ELIGIBLE
    assert result.eligible is False
    codes = [r.code for r in result.reasons]
    assert "AGE_MIN" in codes


def test_not_eligible_above_maximum_amount_when_configured():
    rules = EligibilityRules(rules_version="test", amount_max=100000.0)
    result = EligibilityService().evaluate(
        EligibilityInput(client_age=30, requested_amount=500000.0), rules=rules
    )
    assert result.eligible is False
    assert [r.code for r in result.reasons] == ["AMOUNT_MAX"]


def test_currency_not_allowed_when_configured():
    rules = EligibilityRules(rules_version="test", allowed_currencies=["XOF"])
    result = EligibilityService().evaluate(
        EligibilityInput(requested_amount=1000.0, currency="EUR"), rules=rules
    )
    assert result.eligible is False
    assert [r.code for r in result.reasons] == ["CURRENCY_NOT_ALLOWED"]


def test_product_not_allowed_when_configured():
    rules = EligibilityRules(rules_version="test", allowed_products=["PROD-A"])
    result = EligibilityService().evaluate(
        EligibilityInput(requested_amount=1000.0, product_id="PROD-B"), rules=rules
    )
    assert result.eligible is False
    assert [r.code for r in result.reasons] == ["PRODUCT_NOT_ALLOWED"]


def test_missing_client_age_is_not_eligible_with_age_min():
    rules = EligibilityRules(rules_version="test", age_min=18)
    result = EligibilityService().evaluate(
        EligibilityInput(requested_amount=1000.0, requested_term=12), rules=rules
    )
    assert result.eligible is False
    assert [r.code for r in result.reasons] == ["AGE_MIN"]
