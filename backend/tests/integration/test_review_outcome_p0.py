"""Tests d'integration Review + Outcome (P0, etapes 16-18).

Couvre la file de revue (REVIEW -> PENDING -> ASSIGNED -> COMPLETED) et la
fermeture de boucle outcome (application -> decision -> loan -> outcome).
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

_TRUNCATE_TABLES = (
    "institutions",
    "clients",
    "applications",
    "reviews",
    "loan_outcomes",
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
        db.commit()
    finally:
        db.close()
    yield


def admin_headers(institution_id: str | None = str(INST_A)) -> dict:
    token = create_access_token(subject="admin-user", role="ADMIN", institution_id=institution_id)
    return {"Authorization": f"Bearer {token}"}


def _create_application(client) -> str:
    client_id = client.post(
        "/v1/clients", json={"first_name": "Awa", "last_name": "Diallo"}, headers=admin_headers()
    ).json()["client_id"]
    app = client.post(
        "/v1/applications",
        json={"client_id": client_id, "product_id": "PROD-01", "requested_amount": 500000.0, "requested_term": 12},
        headers=admin_headers(),
    ).json()
    return app["application_id"]


def test_review_queue_lifecycle(client):
    app_id = _create_application(client)
    created = client.post("/v1/reviews", json={"application_id": app_id, "review_reason": "REVIEW policy"}, headers=admin_headers()).json()
    assert created["status"] == "PENDING"
    assert created["application_id"] == app_id
    review_id = created["review_id"]

    queue = client.get("/v1/reviews", headers=admin_headers()).json()
    assert any(r["review_id"] == review_id for r in queue)

    assigned = client.patch(f"/v1/reviews/{review_id}/assign", json={"assigned_to": "officer-1"}, headers=admin_headers()).json()
    assert assigned["status"] == "ASSIGNED"
    assert assigned["assigned_to"] == "officer-1"

    started = client.post(f"/v1/reviews/{review_id}/start", headers=admin_headers()).json()
    assert started["status"] == "IN_PROGRESS"

    completed = client.post(f"/v1/reviews/{review_id}/complete", json={"final_action": "APPROVE"}, headers=admin_headers()).json()
    assert completed["status"] == "COMPLETED"
    assert completed["final_action"] == "APPROVE"


def test_review_tenant_isolation(client):
    app_id = _create_application(client)
    created = client.post("/v1/reviews", json={"application_id": app_id, "review_reason": "iso"}, headers=admin_headers()).json()
    review_id = created["review_id"]
    resp = client.patch(f"/v1/reviews/{review_id}/assign", json={"assigned_to": "x"}, headers=admin_headers(str(uuid.uuid4())))
    assert resp.status_code == 404


def test_outcome_closes_loop(client):
    app_id = _create_application(client)
    outcome = client.post(
        f"/v1/applications/{app_id}/outcomes",
        json={"application_id": app_id, "loan_id": "LOAN-001", "status": "repaid", "default_status": False, "source": "core"},
        headers=admin_headers(),
    ).json()
    assert outcome["application_id"] == app_id
    assert outcome["loan_id"] == "LOAN-001"

    listed = client.get(f"/v1/applications/{app_id}/outcomes", headers=admin_headers()).json()
    assert len(listed) == 1


def test_outcome_tenant_isolation(client):
    app_id = _create_application(client)
    client.post(
        f"/v1/applications/{app_id}/outcomes",
        json={"application_id": app_id, "loan_id": "L2", "status": "defaulted", "default_status": True},
        headers=admin_headers(),
    )
    resp = client.get(f"/v1/applications/{app_id}/outcomes", headers=admin_headers(str(uuid.uuid4())))
    assert resp.json() == []