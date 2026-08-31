"""Tests d'integration de l'eligibilite end-to-end (P0, etape 4).

Couvre la route POST /v1/applications/{id}/eligibility : calcul de l'age du
client, application des regles par defaut et regles injectees, isolation
multi-tenant.
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
INST_B = uuid.uuid4()

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


def _create_application(client, age: int, inst: str = str(INST_A)) -> str:
    dob = datetime(2000, 1, 1).isoformat() if age == 26 else None
    if age is None:
        dob = None
    elif age != 26:
        # date de naissance calculee pour un age approximatif (>= 18)
        year = 2026 - age
        dob = f"{year}-01-01T00:00:00"
    client_id = client.post(
        "/v1/clients",
        json={"first_name": "Awa", "last_name": "Diallo", "date_of_birth": dob},
        headers=admin_headers(inst),
    ).json()["client_id"]
    app = client.post(
        "/v1/applications",
        json={"client_id": client_id, "product_id": "PROD-01", "requested_amount": 500000.0, "requested_term": 12},
        headers=admin_headers(inst),
    ).json()
    return app["application_id"]


def test_eligible_application(client):
    app_id = _create_application(client, age=26)
    response = client.post(f"/v1/applications/{app_id}/eligibility", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ELIGIBLE"
    assert body["eligible"] is True
    assert body["reasons"] == []


def test_not_eligible_underage(client):
    app_id = _create_application(client, age=17)
    response = client.post(f"/v1/applications/{app_id}/eligibility", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NOT_ELIGIBLE"
    assert body["eligible"] is False
    assert [r["code"] for r in body["reasons"]] == ["AGE_MIN"]


def test_custom_rules_via_body(client):
    app_id = _create_application(client, age=26)
    rules = {"rules_version": "test", "amount_max": 100000.0}
    response = client.post(
        f"/v1/applications/{app_id}/eligibility", json=rules, headers=admin_headers()
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NOT_ELIGIBLE"
    assert [r["code"] for r in body["reasons"]] == ["AMOUNT_MAX"]
    assert body["rules_version"] == "test"


def test_eligibility_tenant_isolation(client):
    app_id = _create_application(client, age=26, inst=str(INST_A))
    response = client.post(f"/v1/applications/{app_id}/eligibility", headers=admin_headers(str(INST_B)))
    assert response.status_code in (403, 404)
