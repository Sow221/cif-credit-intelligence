"""Tests unitaires des features (reponse.txt, section 5.1)."""

import math

from src.features.definitions.loan_to_savings import LoanToSavingsFeature
from src.features.definitions.loan_to_income import LoanToIncomeFeature
from src.features.definitions.savings_ratio import SavingsRatioFeature
from src.features.definitions.seniority import SeniorityFeature
from src.features.registry import FeatureRegistry


def test_ratio_normal():
    assert LoanToSavingsFeature.compute(
        {"current_loan_request": 500, "current_savings": 1000}
    ) == 500 / 1001


def test_ratio_zero_savings():
    assert LoanToSavingsFeature.compute(
        {"current_loan_request": 500, "current_savings": 0}
    ) == 500


def test_ratio_zero_request():
    assert LoanToSavingsFeature.compute(
        {"current_loan_request": 0, "current_savings": 1000}
    ) == 0


def test_loan_to_income():
    assert LoanToIncomeFeature.compute(
        {"current_loan_request": 500, "monthly_income": 850}
    ) == 500 / 851


def test_savings_ratio():
    assert SavingsRatioFeature.compute(
        {"current_savings": 1200, "monthly_income": 850}
    ) == 1200 / 851


def test_seniority_years():
    assert SeniorityFeature.compute({"seniority_months": 48}) == 4.0


def test_registry_count_is_25():
    assert FeatureRegistry.count() == 25


def test_registry_derived_mapping():
    assert FeatureRegistry.is_derived("loan_to_savings_ratio")
    assert not FeatureRegistry.is_derived("age")
