from pydantic import BaseModel, EmailStr, Field, model_validator


class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    certificate_id: str = Field(..., min_length=1, max_length=100)


class GenerationJobCreate(BaseModel):
    event_name: str = Field(..., min_length=2, max_length=255)
    recipients: list[RecipientCreate] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_unique_certificate_ids(self):
        certificate_ids = [r.certificate_id for r in self.recipients]

        if len(certificate_ids) != len(set(certificate_ids)):
            raise ValueError("certificate_id values must be unique")

        return self


class GenerationJobResponse(BaseModel):
    job_id: str
    event_name: str
    status: str
    total: int
    completed: int
    failed: int


class RecipientResponse(BaseModel):
    certificate_id: str
    name: str
    email: str
    status: str
    file_path: str | None = None
    error_message: str | None = None


class CertificateResponse(BaseModel):
    certificate_id: str
    name: str
    email: str
    status: str
    download_url: str | None = None
    error_message: str | None = None