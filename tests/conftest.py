import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.dependencies import get_db
from app import models

os.environ["ENV"] = "test"
os.environ.setdefault("SECRET_KEY", "test-secret-key")

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False)

@pytest.fixture(scope="session", autouse=True)
def create_test_schema():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture()
def client(db_session):

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture()
def user_payload():
    return {
        "email":"eric@example.com",
        "username":"eric",
        "password":"supersecret123",
        "timezone":"EST"
    }

@pytest.fixture()
def register_user(client, user_payload):
    res = client.post("/auth/register", json=user_payload)
    assert res.status_code == 201, res.text
    return res.json()

@pytest.fixture()
def access_token(client, user_payload, register_user):
    res = client.post(
        "/auth/login",
        data={"username":user_payload["username"],"password":user_payload["password"]},
        headers={"Content-Type":"application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    assert isinstance(token,str) and len(token)>20
    return token

@pytest.fixture()
def auth_headers(access_token):
    return {"Authorization":f"Bearer {access_token}"}