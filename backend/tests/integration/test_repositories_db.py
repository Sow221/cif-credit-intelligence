from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.governance.consent import ConsentService
from src.governance.lineage import LineageService
from src.models.database import (
    Consent,
    DataSource,
    FeatureSet,
    FeatureSnapshot,
    ModelVersion,
    Prediction,
)
from src.repositories.application_repository import ApplicationRepository
from src.repositories.audit_repository import AuditRepository
from src.repositories.client_repository import ClientRepository
from src.repositories.decision_repository import DecisionRepository
from src.repositories.information_profile_repository import InformationProfileRepository
from src.repositories.outcome_repository import OutcomeRepository
from src.repositories.prediction_repository import PredictionRepository
from src.repositories.review_repository import ReviewRepository


def test_client_repo_create(db, institution):
    repo = ClientRepository(db)
    c = repo.create(institution_id=institution.institution_id, first_name="Ali", last_name="Ndiaye")
    assert c.first_name == "Ali"
    assert c.institution_id == institution.institution_id


def test_client_repo_get_and_list(db, institution):
    repo = ClientRepository(db)
    c = repo.create(institution_id=institution.institution_id, first_name="A", last_name="B")
    found = repo.get_by_id(c.client_id)
    assert found is not None
    all_clients = repo.get_multi(institution.institution_id)
    assert len(all_clients) >= 1


def test_application_repo_create_and_list(db, institution, client):
    repo = ApplicationRepository(db)
    app = repo.create(
        institution_id=institution.institution_id,
        client_id=client.client_id,
        product_id="MICRO_CREDIT",
        requested_amount=500000,
        currency="XOF",
        requested_term=12,
        status="DRAFT",
    )
    assert app.status == "DRAFT"
    found = repo.get_by_id(app.application_id, institution.institution_id)
    assert found is not None
    apps = repo.get_multi(institution.institution_id)
    assert len(apps) >= 1


def test_application_repo_update_status(db, institution, client):
    repo = ApplicationRepository(db)
    app = repo.create(
        institution_id=institution.institution_id,
        client_id=client.client_id,
        product_id="MC",
        requested_amount=100000,
        requested_term=6,
        status="DRAFT",
    )
    updated = repo.update_status(app.application_id, institution.institution_id, "SUBMITTED")
    assert updated is not None
    assert updated.status == "SUBMITTED"


def test_audit_repo_append_only(db, institution, user):
    repo = AuditRepository(db)
    event = repo.create(
        institution_id=institution.institution_id,
        actor_id=user.user_id,
        event_type="LOGIN",
    )
    assert event.event_type == "LOGIN"
    events = repo.get_by_event_type(institution.institution_id, "LOGIN")
    assert len(events) >= 1
    # Verify no update/delete methods exist (append-only)
    assert not hasattr(repo, "update")
    assert not hasattr(repo, "delete")


def test_information_profile_repo(db, institution, application_fixture):
    repo = InformationProfileRepository(db)
    prof = repo.create(
        application_id=application_fixture.application_id,
        institution_id=institution.institution_id,
        applicant_status="ESTABLISHED",
        credit_depth="HIGH",
        financial_depth="MEDIUM",
        business_depth="LOW",
        relationship_depth="NONE",
        data_quality="GOOD",
        information_state="FULL_FILE",
        profile_version=1,
        config_version=1,
    )
    assert prof.information_state == "FULL_FILE"
    got = repo.get_by_application(application_fixture.application_id)
    assert got is not None


def test_prediction_repo(db, institution, application_fixture, model_fixture, snapshot_fixture):
    repo = PredictionRepository(db)
    pred = repo.create(
        application_id=application_fixture.application_id,
        model_version_id=model_fixture.model_version_id,
        snapshot_id=snapshot_fixture.snapshot_id,
        pd_raw=0.5,
        pd_calibrated=0.45,
    )
    assert pred.pd_raw == 0.5
    got = repo.get_by_application(application_fixture.application_id)
    assert got is not None


def test_review_repo_transitions(db, institution, application_fixture, decision_fixture, user):
    repo = ReviewRepository(db)
    review = repo.create(
        application_id=application_fixture.application_id,
        decision_id=decision_fixture.decision_id,
        status="PENDING",
        review_reason="High uncertainty",
    )
    assert review.status == "PENDING"
    repo.assign(review.review_id, user.user_id)
    assert review.status == "ASSIGNED"
    repo.start_review(review.review_id)
    assert review.status == "IN_PROGRESS"
    repo.complete_review(review.review_id, "APPROVE")
    assert review.status == "COMPLETED"


def test_consent_service_lifecycle(
    db, institution, client, application_fixture, data_source_fixture
):
    svc = ConsentService(db)
    with pytest.raises(ValueError):
        svc.create(
            application_fixture.application_id,
            client.client_id,
            institution.institution_id,
            data_source_fixture.source_id,
            "credit_check",
            status="BOGUS",
        )
    consent = svc.create(
        application_fixture.application_id,
        client.client_id,
        institution.institution_id,
        data_source_fixture.source_id,
        "credit_check",
    )
    assert consent.status == "GRANTED"
    found = svc.check_consent(application_fixture.application_id, data_source_fixture.source_id)
    assert found is not None and found.status == "GRANTED"
    revoked = svc.revoke(consent.consent_id)
    assert revoked.status == "REVOKED"
    assert (
        svc.check_consent(application_fixture.application_id, data_source_fixture.source_id) is None
    )


def test_lineage_service(db, institution, application_fixture, data_source_fixture):
    svc = LineageService(db)
    lineage = svc.record(
        application_fixture.application_id,
        data_source_fixture.source_id,
        "monthly_income",
        feature_name="income_ratio",
    )
    assert lineage.field_name == "monthly_income"
    assert svc.is_traceable("income_ratio", application_fixture.application_id)
    assert not svc.is_traceable("unknown_feature", application_fixture.application_id)
    traces = svc.trace(application_fixture.application_id)
    assert len(traces) >= 1


def test_decision_repo_crud(db, institution, decision_fixture):
    repo = DecisionRepository(db)
    found = repo.get_by_id(decision_fixture.decision_id)
    assert found is not None
    got = repo.get_by_application(decision_fixture.application_id)
    assert got is not None
    decs = repo.get_multi(institution.institution_id)
    assert len(decs) >= 1
    updated = repo.update(
        decision_fixture.decision_id,
        institution_id=institution.institution_id,
        recommendation="APPROVE",
    )
    assert updated.recommendation == "APPROVE"
    assert repo.delete(decision_fixture.decision_id) is True
    assert repo.delete(decision_fixture.decision_id) is False


def test_outcome_repo_crud(db, institution, application_fixture):
    repo = OutcomeRepository(db)
    outcome = repo.create(
        application_id=application_fixture.application_id,
        status="PAID_OFF",
        outcome_date=datetime.now(UTC),
        source="LOAN_TRACKING",
    )
    assert outcome.status == "PAID_OFF"
    found = repo.get_by_id(outcome.outcome_id)
    assert found is not None
    got = repo.get_by_application(application_fixture.application_id)
    assert got is not None
    outcomes = repo.get_multi(institution.institution_id)
    assert len(outcomes) >= 1
    updated = repo.update(outcome.outcome_id, days_overdue=5)
    assert updated.days_overdue == 5
    assert repo.delete(outcome.outcome_id) is True


@pytest.fixture
def application_fixture(db, institution, client):
    repo = ApplicationRepository(db)
    return repo.create(
        institution_id=institution.institution_id,
        client_id=client.client_id,
        product_id="MICRO_CREDIT",
        requested_amount=500000,
        currency="XOF",
        requested_term=12,
        status="SCORED",
    )


@pytest.fixture
def data_source_fixture(db, institution):
    ds = DataSource(
        institution_id=institution.institution_id, name="Core Banking", source_type="INTERNAL_SFD"
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds


@pytest.fixture
def consent_fixture(db, institution, client, data_source_fixture):
    c = Consent(
        application_id=uuid.uuid4(),
        client_id=client.client_id,
        institution_id=institution.institution_id,
        source_id=data_source_fixture.source_id,
        purpose="credit_check",
        status="GRANTED",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def feature_set_fixture(db):
    fs = FeatureSet(name="FULL_ADMISSIBLE", description="All features", feature_ids="[]")
    db.add(fs)
    db.commit()
    db.refresh(fs)
    return fs


@pytest.fixture
def model_fixture(db, feature_set_fixture):
    m = ModelVersion(
        model_id="xgb",
        name="XGBoost",
        version="v1.0",
        model_type="XGB",
        feature_set_id=feature_set_fixture.set_id,
        status="PRODUCTION",
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@pytest.fixture
def snapshot_fixture(db, application_fixture, feature_set_fixture):
    snap = FeatureSnapshot(
        application_id=application_fixture.application_id,
        feature_set_id=feature_set_fixture.set_id,
        feature_schema_version="v1",
        features_json="{}",
        input_snapshot_hash="abc123",
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap


@pytest.fixture
def decision_fixture(db, institution, application_fixture, model_fixture, snapshot_fixture):
    from src.models.database import Decision, DecisionPolicy

    policy = DecisionPolicy(
        institution_id=institution.institution_id,
        product_id="MICRO_CREDIT",
        version=1,
        eligibility_rules="{}",
        approve_rule="{}",
        review_rule="{}",
        decline_rule="{}",
        effective_from=datetime.now(UTC),
        status="ACTIVE",
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    pred = Prediction(
        application_id=application_fixture.application_id,
        model_version_id=model_fixture.model_version_id,
        snapshot_id=snapshot_fixture.snapshot_id,
        pd_raw=0.5,
        pd_calibrated=0.45,
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    d = Decision(
        application_id=application_fixture.application_id,
        institution_id=institution.institution_id,
        policy_id=policy.policy_id,
        prediction_id=pred.prediction_id,
        recommendation="REVIEW",
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d
