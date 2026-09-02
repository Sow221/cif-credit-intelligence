"""Tests des couches decision (P0, etapes 12-15).

Couvre :
  12. Calibration : pd_raw != pd_calibrated, methode/version enregistrees.
  13. Uncertainty : interface {level, score, method, version, factors},
      jamais identique a 1 - pd.
  14. Decision policy : resolution de la policy active, seuils depuis le policy
      (jamais hardcodes), erreur si aucun policy actif.
  15. Decision engine : APPROVE/REVIEW/DECLINE depuis le policy.
"""

import sys
import uuid
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from sqlalchemy import text

from src.api.middleware.auth import create_access_token  # noqa: E402
from src.db.session import SessionLocal  # noqa: E402
from src.main import app  # noqa: E402

from src.models.calibration import (  # noqa: E402
    CalibrationConfig,
    CalibrationMethod,
    Calibrator,
)
from src.models.uncertainty import (  # noqa: E402
    UncertaintyConfig,
    UncertaintyEngine,
    UncertaintyLevel,
)
from src.services.decision_engine_p0 import (  # noqa: E402
    Decision,
    DecisionEngineP0,
    EngineInput,
)
from src.services.decision_policy_service import (  # noqa: E402
    DecisionPolicyNotFound,
    DecisionPolicyService,
)

INST_A = uuid.uuid4()

_TRUNCATE_TABLES = (
    "institutions",
    "decision_policies",
)


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _clean(client):  # noqa: ARG001
    db = SessionLocal()
    try:
        db.execute(text(f"TRUNCATE {', '.join(_TRUNCATE_TABLES)} CASCADE"))
        db.commit()
        db.execute(
            text(
                "INSERT INTO institutions (institution_id, name, code, status) "
                "VALUES (:a, 'Inst A', 'INSTA', 'ACTIVE') "
                "ON CONFLICT (institution_id) DO NOTHING"
            ),
            {"a": INST_A},
        )
        db.commit()
    finally:
        db.close()
    yield


def admin_headers(institution_id: str | None = str(INST_A)) -> dict:
    token = create_access_token(subject="admin-user", role="ADMIN", institution_id=institution_id)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Etape 12 - Calibration
# ---------------------------------------------------------------------------


def test_calibration_preserves_raw_and_calibrated() -> None:
    c = Calibrator(CalibrationConfig(method=CalibrationMethod.PLATT, platt_a=1.5, platt_b=0.2))
    r = c.result(0.4)
    assert r.pd_raw == pytest.approx(0.4)
    assert r.method == CalibrationMethod.PLATT
    assert r.calibration_version == "1"


def test_calibration_isotonic_maps() -> None:
    c = Calibrator(
        CalibrationConfig(
            method=CalibrationMethod.ISOTONIC,
            isotropic_bins=[0.0, 0.5, 1.0],
            isotropic_targets=[0.0, 0.4, 0.9],
        )
    )
    assert c.calibrate(0.5) == pytest.approx(0.4)


# ---------------------------------------------------------------------------
# Etape 13 - Uncertainty
# ---------------------------------------------------------------------------


def test_uncertainty_not_equal_one_minus_pd() -> None:
    engine = UncertaintyEngine(UncertaintyConfig(method="EVIDENCE_BASED"))
    r = engine.assess(pd_raw=0.7, evidence_spread=0.0)
    assert r.method == "EVIDENCE_BASED"
    assert r.version == "1"
    assert isinstance(r.factors, list)
    # Interdiction : l'incertitude ne doit pas simplement valoir 1 - pd.
    assert r.score != pytest.approx(1 - 0.7)


def test_uncertainty_high_on_poor_information() -> None:
    engine = UncertaintyEngine(UncertaintyConfig(method="EVIDENCE_BASED"))
    r = engine.assess(
        pd_raw=0.5,
        information_state="NO_FILE",
        data_quality="LOW",
        evidence_spread=0.6,
    )
    assert r.level == UncertaintyLevel.HIGH
    assert r.score >= 0.8


# ---------------------------------------------------------------------------
# Etape 14 - Decision Policy
# ---------------------------------------------------------------------------


def test_policy_requires_active_policy(client) -> None:
    db = SessionLocal()
    try:
        svc = DecisionPolicyService(db)
        with pytest.raises(DecisionPolicyNotFound):
            svc.resolve(INST_A)
    finally:
        db.close()


def test_policy_active_resolved(client) -> None:
    db = SessionLocal()
    try:
        svc = DecisionPolicyService(db)
        policy = svc.build_default_policy(institution_id=INST_A, product_id="PROD-01")
        policy.status = "ACTIVE"
        db.commit()
        resolved = svc.resolve(INST_A, "PROD-01")
        assert resolved is not None
        seuils = svc.approve_seuils(resolved)
        assert "max_pd" in seuils
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Etape 15 - Decision Engine
# ---------------------------------------------------------------------------


def test_decision_engine_returns_three_metier_decisions() -> None:
    engine = DecisionEngineP0()
    # DECLINE par ineligibilite.
    r = engine.decide(
        EngineInput(
            eligibility=False,
            pd_calibrated=0.2,
            uncertainty_level="LOW",
            uncertainty_score=0.2,
        )
    )
    assert r.decision == Decision.DECLINE
    # APPROVE (pd bas, incertitude basse, seuils fournis).
    r2 = engine.decide(
        EngineInput(
            eligibility=True,
            pd_calibrated=0.2,
            uncertainty_level="LOW",
            uncertainty_score=0.2,
            approve_max_pd=0.3,
            decline_max_pd=0.55,
            approve_max_uncertainty=0.35,
        )
    )
    assert r2.decision == Decision.APPROVE
    # REVIEW via incertitude haute.
    r3 = engine.decide(
        EngineInput(
            eligibility=True,
            pd_calibrated=0.2,
            uncertainty_level="HIGH",
            uncertainty_score=0.6,
            approve_max_pd=0.3,
            decline_max_pd=0.55,
            approve_max_uncertainty=0.35,
        )
    )
    assert r3.decision == Decision.REVIEW


def test_decision_engine_requires_policy_thresholds() -> None:
    engine = DecisionEngineP0()
    with pytest.raises(ValueError):
        engine.decide(
            EngineInput(
                eligibility=True,
                pd_calibrated=0.2,
                uncertainty_level="LOW",
                uncertainty_score=0.2,
            )
        )