from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC
from enum import StrEnum
from typing import Any


class QualityStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass
class QualityCheck:
    check_name: str
    status: QualityStatus
    message: str = ""


@dataclass
class QualityReport:
    overall: QualityStatus
    checks: list[QualityCheck] = field(default_factory=list)


class DataQualityService:
    def check(self, records: list[dict[str, Any]]) -> QualityReport:
        checks = []
        checks.append(self._check_schema(records))
        checks.append(self._check_completeness(records))
        checks.append(self._check_validity(records))
        checks.append(self._check_temporal(records))
        overall = QualityStatus.PASS
        for c in checks:
            if c.status == QualityStatus.FAIL:
                overall = QualityStatus.FAIL
                break
            if c.status == QualityStatus.WARNING:
                overall = QualityStatus.WARNING
        return QualityReport(overall=overall, checks=checks)

    def _check_schema(self, records: list[dict[str, Any]]) -> QualityCheck:
        required = {"field_name", "field_value", "data_type", "observed_at", "source_id"}
        for i, r in enumerate(records):
            missing = required - set(r.keys())
            if missing:
                return QualityCheck("schema", QualityStatus.FAIL, f"Record {i}: missing {missing}")
        return QualityCheck("schema", QualityStatus.PASS)

    def _check_completeness(self, records: list[dict[str, Any]]) -> QualityCheck:
        empty = sum(1 for r in records if not r.get("field_value"))
        if empty > len(records) * 0.5:
            return QualityCheck(
                "completeness", QualityStatus.FAIL, f"{empty}/{len(records)} empty values"
            )
        if empty > 0:
            return QualityCheck("completeness", QualityStatus.WARNING, f"{empty} empty values")
        return QualityCheck("completeness", QualityStatus.PASS)

    def _check_validity(self, records: list[dict[str, Any]]) -> QualityCheck:
        return QualityCheck("validity", QualityStatus.PASS)

    def _check_temporal(self, records: list[dict[str, Any]]) -> QualityCheck:
        from datetime import datetime

        now = datetime.now(UTC)
        future = [r for r in records if r.get("observed_at") and r["observed_at"] > now]
        if future:
            return QualityCheck(
                "temporal", QualityStatus.FAIL, f"{len(future)} records with future timestamps"
            )
        return QualityCheck("temporal", QualityStatus.PASS)
