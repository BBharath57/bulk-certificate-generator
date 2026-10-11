from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import GenerationJob, Recipient
from app.schemas.job import (
    GenerationJobCreate,
    GenerationJobResponse,
)
from app.services.job_processor import process_generation_job
from app.schemas.job import CertificateResponse

router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
)


@router.post(
    "/",
    response_model=GenerationJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_generation_job(
    job_data: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = GenerationJob(
        event_name=job_data.event_name,
        status="PENDING",
        total_count=len(job_data.recipients),
    )

    db.add(job)
    db.flush()

    for recipient_data in job_data.recipients:
        recipient = Recipient(
            job_id=job.id,
            name=recipient_data.name,
            email=recipient_data.email,
            certificate_id=recipient_data.certificate_id,
            status="PENDING",
        )

        db.add(recipient)

    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        process_generation_job,
        job.id,
    )

    return GenerationJobResponse(
        job_id=job.id,
        event_name=job.event_name,
        status=job.status,
        total=job.total_count,
        completed=job.success_count,
        failed=job.failure_count,
    )



@router.get(
    "/{job_id}",
    response_model=GenerationJobResponse,
)
def get_generation_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found",
        )

    return GenerationJobResponse(
        job_id=job.id,
        event_name=job.event_name,
        status=job.status,
        total=job.total_count,
        completed=job.success_count,
        failed=job.failure_count,
    )


@router.get(
    "/{job_id}/certificates",
    response_model=list[CertificateResponse],
)
def get_job_certificates(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found",
        )

    recipients = db.query(Recipient).filter(
        Recipient.job_id == job_id
    ).all()

    return [
    CertificateResponse(
        certificate_id=recipient.certificate_id,
        name=recipient.name,
        email=recipient.email,
        status=recipient.status,
        download_url=(
            f"/api/certificates/{recipient.certificate_id}"
            if recipient.status == "COMPLETED"
            else None
        ),
        error_message=recipient.error_message,
    )
    for recipient in recipients
]