# Bulk Certificate Generator

A FastAPI-based backend service for generating completion certificates in bulk from recipient data.

The system accepts a list of recipients, validates the input, creates a background generation job, generates individual PDF certificates, tracks processing progress, handles individual certificate failures without stopping the entire job, and provides endpoints to retrieve generated certificates.

## Features

- Bulk certificate generation
- Recipient data validation using Pydantic
- PostgreSQL database for job and recipient tracking
- Background processing using FastAPI `BackgroundTasks`
- Individual certificate failure handling
- Job status and progress tracking
- PDF certificate generation using ReportLab
- Certificate download endpoint
- Automated tests using Pytest
- API documentation through Swagger UI

## Technology Stack

- **Python**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **Pydantic**
- **ReportLab**
- **Pytest**
- **Uvicorn**

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── api/
│   │   ├── jobs.py
│   │   └── certificates.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   └── job.py
│   │
│   ├── services/
│   │   ├── certificate.py
│   │   └── job_processor.py
│   │
│   ├── storage/
│   │   └── certificates/
│   │
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_certificate.py
│   ├── test_download.py
│   ├── test_job_status.py
│   ├── test_jobs.py
│   ├── test_processing.py
│   └── test_validation.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Database Design

The application uses two main tables.

### GenerationJob

Stores information about a bulk certificate generation job.

Important fields:

- Job ID
- Event name
- Job status
- Total recipients
- Successful certificates
- Failed certificates
- Creation time
- Completion time

### Recipient

Stores information about each certificate recipient.

Important fields:

- Recipient ID
- Job ID
- Name
- Email
- Certificate ID
- Certificate status
- Generated file path
- Error message
- Completion time

A generation job has a one-to-many relationship with recipients.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/BBharath57/bulk-certificate-generator.git
cd bulk-certificate-generator
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database:

```sql
CREATE DATABASE bulk_certificate_db;
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://postgres:<your-password>@localhost:5432/bulk_certificate_db
```

Do not commit the `.env` file.

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Database Health Check

```http
GET /db-health
```

Example response:

```json
{
  "database": true
}
```

### Create Generation Job

```http
POST /api/jobs/
```

Example request:

```json
{
  "event_name": "Python Workshop 2026",
  "recipients": [
    {
      "name": "Bharath",
      "email": "bharath@example.com",
      "certificate_id": "CERT-001"
    },
    {
      "name": "Rahul",
      "email": "rahul@example.com",
      "certificate_id": "CERT-002"
    }
  ]
}
```

Example response:

```json
{
  "job_id": "generated-job-id",
  "event_name": "Python Workshop 2026",
  "status": "PENDING",
  "total": 2,
  "completed": 0,
  "failed": 0
}
```

The job is created immediately and certificate generation is processed in the background.

### Get Job Status

```http
GET /api/jobs/{job_id}
```

Example response:

```json
{
  "job_id": "generated-job-id",
  "event_name": "Python Workshop 2026",
  "status": "COMPLETED",
  "total": 2,
  "completed": 2,
  "failed": 0
}
```

Possible job statuses include:

- `PENDING`
- `PROCESSING`
- `COMPLETED`
- `PARTIALLY_COMPLETED`
- `FAILED`

### Get Certificates for a Job

```http
GET /api/jobs/{job_id}/certificates
```

Example response:

```json
[
  {
    "certificate_id": "CERT-001",
    "name": "Bharath",
    "email": "bharath@example.com",
    "status": "COMPLETED",
    "download_url": "/api/certificates/CERT-001",
    "error_message": null
  }
]
```

### Download Certificate

```http
GET /api/certificates/{certificate_id}
```

Returns the generated certificate as a PDF file.

## Processing Flow

```text
Client
  │
  │ POST /api/jobs/
  ▼
FastAPI
  │
  ├── Validate recipient data
  ├── Create GenerationJob
  ├── Create Recipient records
  │
  └── Start background processing
           │
           ▼
      Job Processor
           │
           ├── Recipient 1 → Certificate → COMPLETED
           ├── Recipient 2 → Certificate → COMPLETED
           ├── Recipient 3 → Error       → FAILED
           │
           ▼
      Update Job Progress
           │
           ▼
   COMPLETED / PARTIALLY_COMPLETED / FAILED
```

Each recipient is processed independently. If certificate generation fails for one recipient, the failure is recorded and processing continues for the remaining recipients.

## Validation

Recipient data is validated before a generation job is created.

The API validates:

- Recipient name
- Email format
- Certificate ID
- At least one recipient
- Unique certificate IDs within a request

Duplicate certificate IDs are rejected during request validation.

## Testing

Run the complete test suite with:

```bash
pytest -v
```

The test suite covers:

- Certificate generation
- Certificate download
- Job creation
- Job status retrieval
- Valid recipient data
- Invalid email validation
- Empty recipient validation
- Duplicate certificate ID validation
- Individual certificate failure handling

Current test result:

```text
9 passed
```

## Design Decisions

### FastAPI BackgroundTasks

FastAPI `BackgroundTasks` is used to process certificates after the job creation request returns.

This keeps the API responsive while allowing the assignment to demonstrate asynchronous-style job processing without introducing additional infrastructure.

### PostgreSQL

PostgreSQL is used as the relational database for persistent job and recipient state.

### Local File Storage

Generated PDFs are stored locally under:

```text
app/storage/certificates/
```

The database stores the generated file path for each successful certificate.

### Failure Isolation

Each recipient is processed inside its own `try/except` block.

Therefore, a failure for one certificate does not terminate the entire bulk generation job.

### Fixed Certificate Template

A predefined certificate layout is generated using ReportLab. Recipient-specific information such as name, event name, certificate ID, and date is inserted into the template.

## Production Considerations

For a production deployment, the following improvements could be considered:

- Use a durable task queue such as Celery/RQ with Redis or another managed queue instead of in-process background tasks.
- Store generated certificates in object storage such as S3 rather than local disk.
- Add authentication and authorization.
- Add rate limiting.
- Add structured logging