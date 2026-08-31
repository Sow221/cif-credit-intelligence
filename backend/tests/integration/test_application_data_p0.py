"""Tests d'integration de l'ingestion des donnees de candidature (P0, etape 3).

Couvre :
- ingestion de donnees brutes reference une source existante
- erreur quand une source referencee n'existe pas (SOURCE_UNAVAILABLE)
- lecture des donnees ingerees (scope tenant)
- isolation multi-tenant : les donnees d'une application ne sont pas vues
  par une autre institution
"""

import sys
import uuid
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
INST_B = uuid.uuid4()
SOURCE_ID = uuid.uuid4()

_TRUNCATE_TABLES = (
    "institutions",
    "clients",
    "applications",
    "application_data",
    "data_sources",
    "audit_events",
    "predictions",
    "decisions",
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
    finally:
        db.close()
    db = SessionLocal()
    try:
        db.execute(
            text(
                "INSERT INTO institutions (institution_id, name, code, status) "
                "VALUES (:a, 'Inst A', 'INSTA', 'ACTIVE'), "
                "(:b, 'Inst B', 'INSTB', 'ACTIVE') "
                "ON CONFLICT (institution_id) DO NOTHING"
            ),
            {"a": INST_A, "b": INST_B},
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


def _create_application(client, inst: str = str(INST_A)) -> str:
    client_id = client.post(
        "/v1/clients", json={"first_name": "Awa", "last_name": "Diallo"},
        headers=admin_headers(inst),
    ).json()["client_id"]
    app = client.post(
        "/v1/applications",
        json={"client_id": client_id, "product_id": "PROD-01", "requested_amount": 500000.0},
        headers=admin_headers(inst),
    ).json()
    return app["application_id"]


def test_ingest_application_data(client):
    app_id = _create_application(client)
    payload = {
        "entries": [
            {"field_name": "monthly_income", "field_value": 250000.0, "source_code": "BANK_STATEMENT"},
            {"field_name": "n_months_history", "field_value": 36, "source_code": "BANK_STATEMENT"},
        ]
    }
    response = client.post(f"/v1/applications/{app_id}/data", json=payload, headers=admin_headers())
    assert response.status_code == 201
    body = response.json()
    assert body["ingested"] == 2
    assert body["sources"] == ["BANK_STATEMENT"]
    assert body["quality_status"] == "PENDING"


def test_ingest_unknown_source_returns_503(client):
    app_id = _create_application(client)
    payload = {
        "entries": [
            {"field_name": "monthly_income", "field_value": 100.0, "source_code": "UNKNOWN_SRC"}
        ]
    }
    response = client.post(f"/v1/applications/{app_id}/data", json=payload, headers=admin_headers())
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SOURCE_UNAVAILABLE"


def test_list_application_data(client):
    app_id = _create_application(client)
    client.post(
        f"/v1/applications/{app_id}/data",
        json={"entries": [{"field_name": "monthly_income", "field_value": 120000.0, "source_code": "BANK_STATEMENT"}]},
        headers=admin_headers(),
    )
    response = client.get(f"/v1/applications/{app_id}/data", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["field_name"] == "monthly_income"
    assert body[0]["quality_status"] == "PENDING"
    assert body[0]["availability_status"] == "AVAILABLE"


def test_ingest_on_missing_application_returns_404(client):
    payload = {"entries": [{"field_name": "x", "field_value": 1, "source_code": "BANK_STATEMENT"}]}
    response = client.post(
        f"/v1/applications/{uuid.uuid4()}/data", json=payload, headers=admin_headers()
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_data_tenant_isolation(client):
    app_id = _create_application(client, str(INST_A))
    client.post(
        f"/v1/applications/{app_id}/data",
        json={"entries": [{"field_name": "monthly_income", "field_value": 1000.0, "source_code": "BANK_STATEMENT"}]},
        headers=admin_headers(str(INST_A)),
    )
    # L'institution B ne voit pas les donnees de A.
    response = client.get(f"/v1/applications/{app_id}/data", headers=admin_headers(str(INST_B)))
    assert response.status_code in (403, 404)
