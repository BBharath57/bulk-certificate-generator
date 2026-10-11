from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas


BASE_DIR = Path(__file__).resolve().parent.parent
CERTIFICATE_DIR = BASE_DIR / "storage" / "certificates"

CERTIFICATE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def generate_certificate(
    recipient_name: str,
    event_name: str,
    certificate_id: str,
) -> str:

    file_path = CERTIFICATE_DIR / f"{certificate_id}.pdf"

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=landscape(A4),
    )

    # Title
    pdf.setFont("Helvetica-Bold", 32)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 100,
        "CERTIFICATE OF COMPLETION",
    )

    # Recipient text
    pdf.setFont("Helvetica", 18)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 180,
        "This certificate is presented to",
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 30)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 240,
        recipient_name,
    )

    # Event
    pdf.setFont("Helvetica", 18)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 300,
        f"for successfully completing {event_name}",
    )

    # Certificate ID
    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        60,
        60,
        f"Certificate ID: {certificate_id}",
    )

    # Date
    pdf.drawRightString(
        page_width - 60,
        60,
        datetime.now().strftime("%d %B %Y"),
    )

    pdf.save()

    return str(file_path)