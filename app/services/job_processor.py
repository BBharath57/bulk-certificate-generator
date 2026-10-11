from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import GenerationJob, Recipient
from app.services.certificate import generate_certificate

from app.db.database import SessionLocal


def process_generation_job(job_id: str):

    db = SessionLocal()

    try:
        job = db.query(GenerationJob).filter(
            GenerationJob.id == job_id
        ).first()

        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        recipients = db.query(Recipient).filter(
            Recipient.job_id == job_id
        ).all()

        for recipient in recipients:

            recipient.status = "PROCESSING"
            db.commit()

            try:
                file_path = generate_certificate(
                    recipient_name=recipient.name,
                    event_name=job.event_name,
                    certificate_id=recipient.certificate_id,
                )

                recipient.status = "COMPLETED"
                recipient.file_path = file_path
                recipient.completed_at = datetime.now(timezone.utc)

                job.success_count += 1

            except Exception as error:

                recipient.status = "FAILED"
                recipient.error_message = str(error)
                recipient.completed_at = datetime.now(timezone.utc)

                job.failure_count += 1

            db.commit()

        if job.failure_count == 0:
            job.status = "COMPLETED"

        elif job.success_count == 0:
            job.status = "FAILED"

        else:
            job.status = "PARTIALLY_COMPLETED"

        job.completed_at = datetime.now(timezone.utc)

        db.commit()

    finally:
        db.close()