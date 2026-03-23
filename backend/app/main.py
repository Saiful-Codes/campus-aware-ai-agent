from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title="Campus-Aware Intelligent AI Agent API")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "port": settings.APP_PORT,
    }