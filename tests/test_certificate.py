from pathlib import Path

from app.services.certificate import generate_certificate


def test_generate_certificate():

    file_path = generate_certificate(
        recipient_name="Bharath",
        event_name="Python Workshop 2026",
        certificate_id="TEST-001",
    )

    path = Path(file_path)

    assert path.exists()
    assert path.is_file()
    assert path.suffix == ".pdf"

    path.unlink()