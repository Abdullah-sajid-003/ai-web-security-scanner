from fastapi import FastAPI

from app.api.routes import auth, scans, targets, vulnerabilities
from app.core.config import settings

app = FastAPI(
    title="AI Web Security Scanner",
    description="Scans websites for vulnerabilities and explains findings in plain English.",
    version="0.1.0",
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.APP_ENV}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(targets.router, prefix="/targets", tags=["targets"])
app.include_router(scans.router, tags=["scans"])
app.include_router(vulnerabilities.router, tags=["vulnerabilities"])
