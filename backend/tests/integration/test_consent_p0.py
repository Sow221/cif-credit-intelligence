"""Tests d'integration du consentement (P0, etape 6).

Couvre : grant/refuse/revoke, guard (allows use when valid, blocks otherwise),
liste scope tenant, et isolation multi-tenant du check.
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

_TRUNCATE_TABLES = ("institutions", "clients", "consents", "audit_events")


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
                "VALUES (:a, 'Inst A', 'INSTA', 'ACTIVE'), "
                "(:b, 'Inst B', 'INSTB', 'ACTIVE') "
                "ON CONFLICT (institution_id) DO NOTHING"
            ),
            {"a": INST_A, "b": INST_B},
        )
        db.commit()
    finally:
        db.close()
    yield


def admin_headers(institution_id: str | None = str(INST_A)) -> dict:
    token = create_access_token(subject="admin-user", role="ADMIN", institution_id=institution_id)
    return {"Authorization": f"Bearer {token}"}


def _create_client(client, inst: str = str(INST_A)) -> str:
    return client.post(
        "/v1/clients", json={"first_name": "Awa", "last_name": "Diallo"},
        headers=admin_headers(inst),
    ).json()["client_id"]


def _record_consent(client, cid, status, inst=str(INST_A)):
    return client.post(
        "/v1/consents",
        json={"client_id": cid, "status": status, "purpose": "credit"},
        headers=admin_headers(inst),
    )


def test_consent_granted_allows_use(client):
    cid = _create_client(client)
    r = _record_consent(client, cid, "GRANTED")
    assert r.status_code == 201
    check = client.get(f"/v1/consents/check?client_id={cid}", headers=admin_headers())
    assert check.status_code == 200
    body = check.json()
    assert body["allowed"] is True
    assert body["status"] == "GRANTED"


def test_consent_not_required_allows_use(client):
    cid = _create_client(client)
    _record_consent(client, cid, "NOT_REQUIRED")
    check = client.get(f"/v1/consents/check?client_id={cid}", headers=admin_headers())
    assert check.json()["allowed"] is True


def test_no_consent_is_unknown_and_blocked(client):
    cid = _create_client(client)
    check = client.get(f"/v1/consents/check?client_id={cid}", headers=admin_headers())
    assert check.status_code == 200
    body = check.json()
    assert body["allowed"] is False
    assert body["status"] == "UNKNOWN"


def test_consent_refused_blocked(client):
    cid = _create_client(client)
    _record_consent(client, cid, "REFUSED")
    check = client.get(f"/v1/consents/check?client_id={cid}", headers=admin_headers())
    assert check.json()["allowed"] is False
    assert check.json()["status"] == "REFUSED"


def test_consent_revoked_blocked(client):
    cid = _create_client(client)
    _record_consent(client, cid, "REVOKED")
    check = client.get(f"/v1/consents/check?client_id={cid}", headers=admin_headers())
    assert check.json()["allowed"] is False
    assert check.json()["status"] == "REVOKED"


def test_list_consents_scope_tenant(client):
    cid = _create_client(client)
    _record_consent(client, cid, "GRANTED")
    _record_consent(client, cid, "NOT_REQUIRED")
    response = client.get(f"/v1/consents?client_id={cid}", headers=admin_headers())
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_consent_check_tenant_isolation(client):
    cid = _create_client(client, str(INST_A))
    # L'institution B ne peut pas consulter le consentement d'un client de A.
    response = client.get(f"/v1/consents/check?client_id={cid}", headers=admin_headers(str(INST_B)))
    assert response.status_code == 404
