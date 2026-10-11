from fastapi import FastAPI, APIRouter, BackgroundTasks, Depends, status
from sqlalchemy import text

from app.db.database import Base, engine
from app.db import models

from app.api.jobs import router as jobs_router
from app.api.certificates import router as certificates_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Bulk Certificate Generator",
    description="Backend API for bulk certificate generation",
    version="1.0.0",
)

app.include_router(jobs_router)
app.include_router(certificates_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/db-health")
def db_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        return {
            "database": result.scalar() == 1
        }



