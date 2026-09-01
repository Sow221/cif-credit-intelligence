"""Tests d'integration des feature snapshots (P0, etape 10).

Couvre la creation d'un snapshot immuable via POST /v1/applications/{id}/snapshot,
la lecture du dernier snapshot et l'isolation tenant. Le snapshot fige
feature_set_id, feature_schema_version, features_json et input_snapshot_hash.
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

INST_A = uuid.uuid4()
SOURCE_ID = uuid.uuid4()

_TRUNCATE_TABLES = (
    "institutions",
    "clients",
    "applications",
    "application_data",
    "data_sources",
    "consents",
    "information_profiles",
    "feature_snapshots",
    "audit_events",
    "data_lineage",
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


def _create_application(client) -> str:
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


def _ingest(client, app_id):
    response = client.post(
        f"/v1/applications/{app_id}/data",
        json={"entries": [
            {"field_name": "monthly_income", "field_value": 250000.0,
             "source_code": "BANK_STATEMENT"},
            {"field_name": "age", "field_value": 34.0,
             "source_code": "BANK_STATEMENT"},
        ]},
        headers=admin_headers(),
    )
    assert response.status_code == 201


def test_snapshot_created_and_persisted(client):
    app_id = _create_application(client)
    _ingest(client, app_id)

    response = client.post(f"/v1/applications/{app_id}/snapshot", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["application_id"] == app_id
    assert body["feature_set_id"] in (
        "MINIMAL", "BUSINESS", "FINANCIAL", "CREDIT", "ALTERNATIVE", "FULL_ADMISSIBLE",
    )
    assert body["feature_schema_version"] == "1"
    assert body["input_snapshot_hash"]
    assert "monthly_income" in body["features"]

    db = SessionLocal()
    row = db.execute(
        text("SELECT feature_snapshot_id FROM feature_snapshots LIMIT 1")
    ).fetchone()
    assert row is not None
    db.close()


def test_snapshot_hash_is_immutable_and_deterministic(client):
    app_id = _create_application(client)
    _ingest(client, app_id)

    first = client.post(f"/v1/applications/{app_id}/snapshot", headers=admin_headers()).json()
    second = client.post(f"/v1/applications/{app_id}/snapshot", headers=admin_headers()).json()

    # meme input pour une meme application -> hash identique (deterministe).
    assert first["input_snapshot_hash"] == second["input_snapshot_hash"]


def test_latest_snapshot_retrieved(client):
    app_id = _create_application(client)
    _ingest(client, app_id)
    client.post(f"/v1/applications/{app_id}/snapshot", headers=admin_headers())

    response = client.get(f"/v1/applications/{app_id}/snapshot/latest", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["application_id"] == app_id
    assert body["feature_snapshot_id"]


def test_snapshot_tenant_isolation(client):
    app_id = _create_application(client)
    _ingest(client, app_id)
    client.post(f"/v1/applications/{app_id}/snapshot", headers=admin_headers())

    response = client.get(
        f"/v1/applications/{app_id}/snapshot/latest",
        headers=admin_headers(str(uuid.uuid4())),
    )
    assert response.status_code == 404