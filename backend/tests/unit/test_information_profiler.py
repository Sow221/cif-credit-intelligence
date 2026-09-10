from __future__ import annotations

from src.features.information_profiler import (
    ApplicantStatus,
    InformationProfilerService,
    InformationState,
)


def test_new_to_institution():
    service = InformationProfilerService()
    result = service.profile([], {"total_applications": 0, "total_loans": 0})
    assert result.applicant_status == ApplicantStatus.NEW_TO_INSTITUTION.value
    assert result.information_state == InformationState.NO_FILE.value


def test_thin_file():
    service = InformationProfilerService()
    data = [{"field_name": "income", "field_value": "500000", "data_type": "financial"}]
    result = service.profile(data, {"total_applications": 5, "total_loans": 3})
    assert result.applicant_status == ApplicantStatus.ESTABLISHED.value
    assert result.information_state == InformationState.THIN_FILE.value


def test_full_file():
    service = InformationProfilerService()
    data = [
        {"field_name": f"field_{i}", "field_value": "value", "data_type": "financial"}
        for i in range(10)
    ]
    result = service.profile(data, {"total_applications": 5, "total_loans": 3})
    assert result.information_state == InformationState.FULL_FILE.value
