from pathlib import Path

from app.db.models import GenerationJob, Recipient


def test_download_generated_certificate(client, db, tmp_path):
    job = GenerationJob(
        event_name="Python Workshop",
        status="COMPLETED",
        total_count=1,
        success_count=1,
        failure_count=0,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    certificate_file = tmp_path / "CERT-999.pdf"
    certificate_file.write_bytes(b"%PDF-1.4 test certificate")

    recipient = Recipient(
        job_id=job.id,
        name="Bharath",
        email="bharath@example.com",
        certificate_id="CERT-999",
        status="COMPLETED",
        file_path=str(certificate_file),
    )

    db.add(recipient)
    db.commit()

    response = client.get("/api/certificates/CERT-999")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content == b"%PDF-1.4 test certificate"