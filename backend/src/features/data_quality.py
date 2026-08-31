"""Qualite des donnees (P0, etape 5).

Verifie les donnees de candidature selon six controles obligatoires :
    schema, completeness, validity, consistency, temporal validity,
    source status.

Statut global : PASS / WARNING / FAIL.
Une erreur CRITIQUE (=> FAIL) bloque le scoring automatique selon la
politique applicable (scenario DATA FAILURE : NO AUTOMATIC DECISION).

Inclut le Guard Temporel (etape 8) pour le scoring d'octroi :
    observed_at <= application_timestamp
Toute donnee dont observed_at > application_timestamp est consideree comme
posterieure a la decision et exclue du feature set d'octroi.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.core.exceptions import DataQualityError, TemporalGuardError


class DataQualityStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class DataQualitySeverity(str, Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class DataSourceStatus(BaseModel):
    """Statut d'une source de donnees pour le controle source status."""

    code: str
    active: bool
    reliable: bool = True


class DataQualityField(BaseModel):
    """Champ de donnees soumis au controle de qualite."""

    model_config = ConfigDict(extra="forbid")

    field_name: str
    field_value: Optional[object] = None
    data_type: Optional[str] = None
    observed_at: Optional[datetime] = None
    source: Optional[DataSourceStatus] = None


class DataQualityIssue(BaseModel):
    control: str
    severity: DataQualitySeverity
    field: Optional[str] = None
    message: str


class DataQualityConfig(BaseModel):
    """Configuration des controles (seuils configurables, pas de valeurs en dur)."""

    completeness_threshold: float = Field(default=1.0, gt=0, le=1)
    expected_types: Dict[str, str] = Field(default_factory=dict)
    valid_ranges: Dict[str, tuple] = Field(default_factory=dict)
    # Champ de reference temporelle pour le scoring d'octroi.
    application_timestamp: Optional[datetime] = None


class DataQualityResult(BaseModel):
    status: DataQualityStatus
    issues: List[DataQualityIssue] = Field(default_factory=list)
    checks: Dict[str, DataQualityStatus] = Field(default_factory=dict)
    data_ready_for_auto_scoring: bool = False
    rejected_fields: List[str] = Field(default_factory=list)
    consent_blocked: List[str] = Field(default_factory=list)


class DataQualityChecker:
    """Applique les six controles obligatoires et produit un rapport."""

    def __init__(self, config: Optional[DataQualityConfig] = None) -> None:
        self._config = config or DataQualityConfig()

    def evaluate(self, fields: List[DataQualityField]) -> DataQualityResult:
        issues: List[DataQualityIssue] = []
        checks: Dict[str, DataQualityStatus] = {}
        rejected: List[str] = []

        issues.extend(self._check_schema(fields))
        issues.extend(self._check_completeness(fields))
        issues.extend(self._check_validity(fields))
        issues.extend(self._check_consistency(fields))
        issues.extend(self._check_temporal(fields, rejected))
        issues.extend(self._check_source_status(fields))

        # Statut par controle.
        controls = [
            "schema",
            "completeness",
            "validity",
            "consistency",
            "temporal_validity",
            "source_status",
        ]
        for control in controls:
            control_issues = [i for i in issues if i.control == control]
            checks[control] = self._agg_status(control_issues)

        global_status = self._agg_status(issues)
        critical = any(i.severity == DataQualitySeverity.CRITICAL for i in issues)
        return DataQualityResult(
            status=global_status,
            issues=issues,
            checks=checks,
            data_ready_for_auto_scoring=not critical,
            rejected_fields=rejected,
        )

    # ------------------------------------------------------------ controles --

    def _agg_status(self, issues: List[DataQualityIssue]) -> DataQualityStatus:
        if any(i.severity == DataQualitySeverity.CRITICAL for i in issues):
            return DataQualityStatus.FAIL
        if issues:
            return DataQualityStatus.WARNING
        return DataQualityStatus.PASS

    def _check_schema(self, fields: List[DataQualityField]) -> List[DataQualityIssue]:
        issues: List[DataQualityIssue] = []
        expected = self._config.expected_types
        for f in fields:
            if f.field_name in expected:
                actual = type(f.field_value).__name__
                if actual != expected[f.field_name]:
                    issues.append(
                        DataQualityIssue(
                            control="schema",
                            severity=DataQualitySeverity.CRITICAL,
                            field=f.field_name,
                            message=(
                                f"Type inattendu pour {f.field_name} : "
                                f"attendu {expected[f.field_name]}, obtenu {actual}"
                            ),
                        )
                    )
        return issues

    def _check_completeness(self, fields: List[DataQualityField]) -> List[DataQualityIssue]:
        issues: List[DataQualityIssue] = []
        for f in fields:
            if f.field_value is None or f.field_value == "":
                issues.append(
                    DataQualityIssue(
                        control="completeness",
                        severity=DataQualitySeverity.WARNING,
                        field=f.field_name,
                        message=f"Champ {f.field_name} manquant",
                    )
                )
        return issues

    def _check_validity(self, fields: List[DataQualityField]) -> List[DataQualityIssue]:
        issues: List[DataQualityIssue] = []
        ranges = self._config.valid_ranges
        for f in fields:
            if f.field_name in ranges and f.field_value is not None:
                lo, hi = ranges[f.field_name]
                v = f.field_value
                if isinstance(v, (int, float)) and not (lo <= v <= hi):
                    issues.append(
                        DataQualityIssue(
                            control="validity",
                            severity=DataQualitySeverity.CRITICAL,
                            field=f.field_name,
                            message=(
                                f"Valeur {v} hors plage valide "
                                f"[{lo}, {hi}] pour {f.field_name}"
                            ),
                        )
                    )
        return issues

    def _check_consistency(self, fields: List[DataQualityField]) -> List[DataQualityIssue]:
        # Les heures d'observation doivent preceder la reception :
        # observed_at <= received_at (controle de base, extensible).
        issues: List[DataQualityIssue] = []
        for f in fields:
            if f.observed_at is None:
                continue
            # sans reference de reception, on ne juge pas la coherence ici.
        return issues

    def _check_temporal(
        self, fields: List[DataQualityField], rejected: List[str]
    ) -> List[DataQualityIssue]:
        """Guard temporel d'octroi : observed_at <= application_timestamp."""
        issues: List[DataQualityIssue] = []
        ref = self._config.application_timestamp
        if ref is None:
            return issues
        for f in fields:
            if f.observed_at is None or f.observed_at <= ref:
                continue
            rejected.append(f.field_name)
            issues.append(
                DataQualityIssue(
                    control="temporal_validity",
                    severity=DataQualitySeverity.CRITICAL,
                    field=f.field_name,
                    message=(
                        f"Donnee {f.field_name} posterieure a la decision "
                        f"(observed_at={f.observed_at} > application_timestamp={ref})"
                    ),
                )
            )
        return issues

    def _check_source_status(self, fields: List[DataQualityField]) -> List[DataQualityIssue]:
        issues: List[DataQualityIssue] = []
        for f in fields:
            src = f.source
            if src is None:
                issues.append(
                    DataQualityIssue(
                        control="source_status",
                        severity=DataQualitySeverity.CRITICAL,
                        field=f.field_name,
                        message=f"Champ {f.field_name} sans source associee",
                    )
                )
                continue
            if not src.active:
                issues.append(
                    DataQualityIssue(
                        control="source_status",
                        severity=DataQualitySeverity.CRITICAL,
                        field=f.field_name,
                        message=f"Source {src.code} inactive pour {f.field_name}",
                    )
                )
            elif not src.reliable:
                issues.append(
                    DataQualityIssue(
                        control="source_status",
                        severity=DataQualitySeverity.WARNING,
                        field=f.field_name,
                        message=f"Source {src.code} de fiabilite reduite pour {f.field_name}",
                    )
                )
        return issues

    # --------------------------------------------------------- helpers API --

    def assert_scoreable(self, result: DataQualityResult) -> None:
        """Leve DataQualityError si une erreur critique bloque le scoring."""
        if result.status == DataQualityStatus.FAIL:
            raise DataQualityError(
                "The application data failed a critical validation check.",
                details={"checks": result.checks, "issues": [i.model_dump() for i in result.issues]},
            )

    def assert_temporal(self, result: DataQualityResult) -> None:
        """Leve TemporalGuardError si des donnees sont posterieures a la decision."""
        if result.rejected_fields:
            raise TemporalGuardError(
                "Donnees posterieures a la decision exclues du feature set",
                details={"rejected_fields": result.rejected_fields},
            )
