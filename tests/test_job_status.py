from app.db.models import GenerationJob, Recipient
from tests.conftest import TestingSessionLocal


def test_get_job_status(client):
    db = TestingSessionLocal()

    job = GenerationJob(
        event_name="Python Workshop",
        status="PROCESSING",
        total_count=3,
        success_count=2,
        failure_count=1,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    response = client.get(f"/api/jobs/{job.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job.id
    assert data["event_name"] == "Python Workshop"
    assert data["status"] == "PROCESSING"
    assert data["total"] == 3
    assert data["completed"] == 2
    assert data["failed"] == 1

    db.close()