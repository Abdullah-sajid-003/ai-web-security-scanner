from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title="AI Web Security Scanner",
    description="Scans websites for vulnerabilities and explains findings in plain English.",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.APP_ENV}
