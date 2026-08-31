"""Tests d'integration de la validation de qualite des donnees (P0, etape 5/8).

Couvre la route POST /v1/applications/{id}/data/validate : PASS par defaut,
FAIL quand la source est inactive, et rejet temporel des donnees posterieures
a la decision (guard d'octroi).
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.api.middleware.auth import create_access_token  # noqa: E402
from src.db.session import SessionLocal  # noqa: E402
from src.main import app  # noqa: E402

INST_A = uuid.uuid4()
SOURCE_ID = uuid.uuid4()

_TRUNCATE_TABLES = (
    "institutions",
    "clients",
    "applications",
    "application_data",
    "data_sources",
    "audit_events",
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
        db.execute(
            text(
                "INSERT INTO data_sources (source_id, code, type, name, active) "
                "VALUES (:s, 'BANK_STATEMENT', 'BANK', 'Etat bancaire', TRUE) "
                "ON CONFLICT (source_id) DO NOTHING"
            ),
            {"s": SOURCE_ID},
        )
        db.commit()
    finally:
        db.close()
    yield


def admin_headers(institution_id: str | None = str(INST_A)) -> dict:
    token = create_access_token(subject="admin-user", role="ADMIN", institution_id=institution_id)
    return {"Authorization": f"Bearer {token}"}


def _create_application(client) -> tuple[str, str]:
    client_id = client.post(
        "/v1/clients", json={"first_name": "Awa", "last_name": "Diallo"},
        headers=admin_headers(),
    ).json()["client_id"]
    app = client.post(
        "/v1/applications",
        json={"client_id": client_id, "product_id": "PROD-01",
              "requested_amount": 500000.0, "requested_term": 12},
        headers=admin_headers(),
    ).json()
    return app["application_id"]


def _ingest(client, app_id, observed_at: str | None = None):
    entry = {
        "field_name": "monthly_income",
        "field_value": 250000.0,
        "source_code": "BANK_STATEMENT",
    }
    if observed_at:
        entry["observed_at"] = observed_at
    response = client.post(
        f"/v1/applications/{app_id}/data",
        json={"entries": [entry]},
        headers=admin_headers(),
    )
    assert response.status_code == 201


def test_validate_pass(client):
    app_id = _create_application(client)
    _ingest(client, app_id)
    response = client.post(f"/v1/applications/{app_id}/data/validate", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PASS"
    assert body["data_ready_for_auto_scoring"] is True
    assert body["checks"]["source_status"] == "PASS"


def test_validate_fail_when_source_inactive(client):
    app_id = _create_application(client)
    _ingest(client, app_id)
    db = SessionLocal()
    try:
        db.execute(text("UPDATE data_sources SET active = FALSE WHERE source_id = :s"), {"s": SOURCE_ID})
        db.commit()
    finally:
        db.close()
    response = client.post(f"/v1/applications/{app_id}/data/validate", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FAIL"
    assert body["data_ready_for_auto_scoring"] is False
    assert body["checks"]["source_status"] == "FAIL"


def test_validate_temporal_rejects_future_data(client):
    app_id = _create_application(client)
    _ingest(client, app_id, observed_at="2026-12-01T00:00:00")
    # Fixe le timestamp d'octroi de l'application avant la donnee observee.
    db = SessionLocal()
    try:
        db.execute(
            text("UPDATE applications SET application_timestamp = :ts WHERE application_id = :a"),
            {"ts": datetime(2026, 1, 1), "a": uuid.UUID(app_id)},
        )
        db.commit()
    finally:
        db.close()
    response = client.post(f"/v1/applications/{app_id}/data/validate", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FAIL"
    assert body["data_ready_for_auto_scoring"] is False
    assert "monthly_income" in body["rejected_fields"]
