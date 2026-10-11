from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_db
from tests.conftest import TestingSessionLocal
from app.db.database import Base
from tests.conftest import engine


def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


def test_create_generation_job(client, monkeypatch):

    monkeypatch.setattr(
        "app.api.jobs.process_generation_job",
        lambda job_id: None,
    )

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop 2026",
            "recipients": [
                {
                    "name": "Bharath",
                    "email": "bharath@example.com",
                    "certificate_id": "TEST-CERT-001",
                },
                {
                    "name": "Rahul",
                    "email": "rahul@example.com",
                    "certificate_id": "TEST-CERT-002",
                },
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_name"] == "Python Workshop 2026"
    assert data["status"] == "PENDING"
    assert data["total"] == 2