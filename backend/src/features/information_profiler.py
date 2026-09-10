from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Depth(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InformationState(StrEnum):
    NO_FILE = "NO_FILE"
    THIN_FILE = "THIN_FILE"
    FULL_FILE = "FULL_FILE"
    DATA_POOR = "DATA_POOR"
    UNKNOWN = "UNKNOWN"


class ApplicantStatus(StrEnum):
    NEW_TO_INSTITUTION = "NEW_TO_INSTITUTION"
    NEW_TO_CREDIT = "NEW_TO_CREDIT"
    ESTABLISHED = "ESTABLISHED"


@dataclass
class InformationProfileConfig:
    version: int = 1
    new_to_institution_threshold: int = 1
    new_to_credit_threshold: int = 0
    thin_file_min_fields: int = 3
    full_file_min_fields: int = 8
    data_poor_quality_threshold: float = 0.5


DEFAULT_CONFIG = InformationProfileConfig()


@dataclass
class ProfileResult:
    applicant_status: str
    credit_depth: str
    financial_depth: str
    business_depth: str
    relationship_depth: str
    data_quality: str
    information_state: str
    profile_version: int
    config_version: int


class InformationProfilerService:
    def __init__(self, config: InformationProfileConfig | None = None):
        self.config = config or DEFAULT_CONFIG

    def profile(
        self, application_data: list[dict[str, Any]], client_history: dict[str, Any] | None = None
    ) -> ProfileResult:
        history = client_history or {}
        total_apps = history.get("total_applications", 0)
        total_loans = history.get("total_loans", 0)
        if total_apps <= self.config.new_to_institution_threshold:
            applicant_status = ApplicantStatus.NEW_TO_INSTITUTION.value
        elif total_loans <= self.config.new_to_credit_threshold:
            applicant_status = ApplicantStatus.NEW_TO_CREDIT.value
        else:
            applicant_status = ApplicantStatus.ESTABLISHED.value
        credit_depth = self._assess_depth(application_data, "credit")
        financial_depth = self._assess_depth(application_data, "financial")
        business_depth = self._assess_depth(application_data, "business")
        relationship_depth = self._assess_depth(application_data, "relationship")
        data_quality = self._assess_quality(application_data)
        information_state = self._determine_state(application_data, data_quality)
        return ProfileResult(
            applicant_status=applicant_status,
            credit_depth=credit_depth,
            financial_depth=financial_depth,
            business_depth=business_depth,
            relationship_depth=relationship_depth,
            data_quality=data_quality,
            information_state=information_state,
            profile_version=1,
            config_version=self.config.version,
        )

    def _assess_depth(self, data: list[dict[str, Any]], group: str) -> str:
        group_fields = [d for d in data if d.get("data_type", "").startswith(group)]
        count = len(group_fields)
        if count == 0:
            return Depth.NONE.value
        if count <= 2:
            return Depth.LOW.value
        if count <= 5:
            return Depth.MEDIUM.value
        return Depth.HIGH.value

    def _assess_quality(self, data: list[dict[str, Any]]) -> str:
        if not data:
            return "POOR"
        valid = sum(1 for d in data if d.get("field_value"))
        ratio = valid / len(data)
        if ratio >= 0.8:
            return "GOOD"
        if ratio >= 0.5:
            return "FAIR"
        return "POOR"

    def _determine_state(self, data: list[dict[str, Any]], quality: str) -> str:
        count = len(data)
        if count == 0:
            return InformationState.NO_FILE.value
        if quality == "POOR":
            return InformationState.DATA_POOR.value
        if count < self.config.thin_file_min_fields:
            return InformationState.THIN_FILE.value
        if count >= self.config.full_file_min_fields:
            return InformationState.FULL_FILE.value
        return InformationState.THIN_FILE.value
