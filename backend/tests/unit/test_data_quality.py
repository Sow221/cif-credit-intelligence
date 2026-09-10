from __future__ import annotations

from src.features.data_quality import DataQualityService, QualityStatus


def test_quality_pass():
    service = DataQualityService()
    records = [
        {
            "field_name": "income",
            "field_value": "500000",
            "data_type": "financial",
            "observed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            "source_id": __import__("uuid").uuid4(),
        },
        {
            "field_name": "savings",
            "field_value": "100000",
            "data_type": "financial",
            "observed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            "source_id": __import__("uuid").uuid4(),
        },
    ]
    report = service.check(records)
    assert report.overall in (QualityStatus.PASS, QualityStatus.WARNING)


def test_quality_fail_missing_fields():
    service = DataQualityService()
    records = [{"field_name": "income"}]
    report = service.check(records)
    assert report.overall == QualityStatus.FAIL


def test_quality_fail_empty_values():
    service = DataQualityService()
    records = [
        {
            "field_name": "income",
            "field_value": "",
            "data_type": "financial",
            "observed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            "source_id": __import__("uuid").uuid4(),
        },
        {
            "field_name": "savings",
            "field_value": "",
            "data_type": "financial",
            "observed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            "source_id": __import__("uuid").uuid4(),
        },
        {
            "field_name": "debt",
            "field_value": "",
            "data_type": "financial",
            "observed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            "source_id": __import__("uuid").uuid4(),
        },
    ]
    report = service.check(records)
    assert report.overall == QualityStatus.FAIL
