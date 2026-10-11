from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Recipient


router = APIRouter(
    prefix="/api/certificates",
    tags=["Certificates"],
)


@router.get("/{certificate_id}")
def download_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    recipient = db.query(Recipient).filter(
        Recipient.certificate_id == certificate_id
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found",
        )

    if recipient.status != "COMPLETED":
        raise HTTPException(
            status_code=409,
            detail="Certificate has not been generated",
        )

    if not recipient.file_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found",
        )

    file_path = Path(recipient.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found on server",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name,
    )