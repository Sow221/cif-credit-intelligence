from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.models.database import (
    Client,
    Consent,
    DataSource,
    Decision,
    DecisionPolicy,
    FeatureSet,
    FeatureSnapshot,
    Institution,
    ModelVersion,
    Prediction,
    User,
)

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def institution(db):
    inst = Institution(name="Test Bank", code="TEST")
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


@pytest.fixture
def user(db, institution):
    u = User(
        institution_id=institution.institution_id,
        email="officer@test.com",
        hashed_password="x",
        full_name="Officer",
        role="CREDIT_OFFICER",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def client(db, institution):
    c = Client(institution_id=institution.institution_id, first_name="Moussa", last_name="Sow")
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def application_fixture(db, institution, client):
    from src.repositories.application_repository import ApplicationRepository

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
        institution_id=institution.institution_id,
        name="Core Banking",
        source_type="INTERNAL_SFD",
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds


@pytest.fixture
def consent_fixture(db, institution, client, data_source_fixture, application_fixture):
    c = Consent(
        application_id=application_fixture.application_id,
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
