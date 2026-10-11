from app.db.models import GenerationJob, Recipient
from app.services.job_processor import process_generation_job
from tests.conftest import TestingSessionLocal


def test_individual_certificate_failure(monkeypatch, db):

    job = GenerationJob(
        event_name="Python Workshop",
        status="PENDING",
        total_count=3,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    recipients = [
        Recipient(
            job_id=job.id,
            name="Bharath",
            email="bharath@example.com",
            certificate_id="CERT-101",
            status="PENDING",
        ),
        Recipient(
            job_id=job.id,
            name="Rahul",
            email="rahul@example.com",
            certificate_id="CERT-102",
            status="PENDING",
        ),
        Recipient(
            job_id=job.id,
            name="Anil",
            email="anil@example.com",
            certificate_id="CERT-103",
            status="PENDING",
        ),
    ]

    db.add_all(recipients)
    db.commit()

    def fake_generate_certificate(
        recipient_name,
        event_name,
        certificate_id,
    ):
        if certificate_id == "CERT-102":
            raise Exception("Simulated certificate generation failure")

        return f"/fake/path/{certificate_id}.pdf"

    monkeypatch.setattr(
        "app.services.job_processor.generate_certificate",
        fake_generate_certificate,
    )

    monkeypatch.setattr(
        "app.services.job_processor.SessionLocal",
        TestingSessionLocal,
    )

    process_generation_job(job.id)

    db.expire_all()

    updated_job = db.query(GenerationJob).filter(
        GenerationJob.id == job.id
    ).first()

    updated_recipients = db.query(Recipient).filter(
        Recipient.job_id == job.id
    ).order_by(Recipient.certificate_id).all()

    assert updated_job.status == "PARTIALLY_COMPLETED"
    assert updated_job.success_count == 2
    assert updated_job.failure_count == 1

    assert updated_recipients[0].status == "COMPLETED"
    assert updated_recipients[1].status == "FAILED"
    assert updated_recipients[2].status == "COMPLETED"

    assert updated_recipients[1].error_message == (
        "Simulated certificate generation failure"
    )

    