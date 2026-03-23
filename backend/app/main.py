from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title="Campus-Aware Intelligent AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for Sprint 1 local setup
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "port": settings.APP_PORT,
    }