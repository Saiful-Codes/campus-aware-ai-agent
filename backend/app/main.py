from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.chat import router as chat_router

app = FastAPI(title="Campus-Aware Intelligent AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "port": settings.APP_PORT,
    }