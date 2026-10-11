import pytest
from pydantic import ValidationError

from app.schemas.job import (
    GenerationJobCreate,
)


def test_valid_generation_job():

    data = GenerationJobCreate(
        event_name="Python Workshop",
        recipients=[
            {
                "name": "Bharath",
                "email": "bharath@example.com",
                "certificate_id": "CERT-001",
            }
        ],
    )

    assert data.event_name == "Python Workshop"
    assert len(data.recipients) == 1


def test_invalid_email():

    with pytest.raises(ValidationError):

        GenerationJobCreate(
            event_name="Python Workshop",
            recipients=[
                {
                    "name": "Bharath",
                    "email": "invalid-email",
                    "certificate_id": "CERT-001",
                }
            ],
        )


def test_empty_recipients():

    with pytest.raises(ValidationError):

        GenerationJobCreate(
            event_name="Python Workshop",
            recipients=[],
        )


def test_duplicate_certificate_ids():
    with pytest.raises(ValidationError):
        GenerationJobCreate(
            event_name="Python Workshop",
            recipients=[
                {
                    "name": "Bharath",
                    "email": "bharath@example.com",
                    "certificate_id": "CERT-001",
                },
                {
                    "name": "Rahul",
                    "email": "rahul@example.com",
                    "certificate_id": "CERT-001",
                },
            ],
        )