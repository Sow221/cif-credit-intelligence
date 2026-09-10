from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UncertaintyResult:
    level: str
    score: float
    method: str
    version: str
    factors: list[dict[str, Any]] = field(default_factory=list)


class UncertaintyService:
    """Evidence-based uncertainty. NEVER uses 1-PD."""

    def assess(self, pd_raw: float, features: dict[str, Any]) -> UncertaintyResult:
        factors = []
        score = 0.0
        missing_count = sum(1 for v in features.values() if v == 0 or v == 0.0)
        total = len(features) if features else 1
        missing_ratio = missing_count / total
        if missing_ratio > 0.3:
            score += missing_ratio * 0.4
            factors.append({"type": "data_completeness", "impact": missing_ratio})
        if pd_raw < 0.1 or pd_raw > 0.9:
            factors.append({"type": "extreme_prediction", "impact": 0.1})
            score += 0.1
        stability = features.get("income_stability", 0.5)
        if stability < 0.3:
            score += 0.15
            factors.append({"type": "income_instability", "impact": 0.15})
        score = min(1.0, max(0.0, score))
        if score < 0.2:
            level = "LOW"
        elif score < 0.5:
            level = "MEDIUM"
        else:
            level = "HIGH"
        return UncertaintyResult(
            level=level,
            score=round(score, 4),
            method="EVIDENCE_BASED",
            version="1.0",
            factors=factors,
        )
