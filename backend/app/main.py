import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.chat import router as chat_router
from app.api import sensor
from app.services.navigation_bootstrap_service import ensure_navigation_data_ready
from app.services.sensor_scheduler import run_sensor_ingestion_loop

try:
    from app.api.rag_chat import router as rag_router
except Exception:
    rag_router = None

# Give user-defined loggers (app.*) a visible output path.
# uvicorn's dictConfig only wires uvicorn.* loggers; the root logger gets no
# handler by default, so any logger.info() in our code is silently dropped.
# basicConfig is a no-op if handlers already exist, so this is safe to call here.
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.APP_ENV in {"production", "staging"}:
        logger.info(
            "Backend starting in %s — validating required env vars.",
            settings.APP_ENV,
        )
        settings.validate_required(strict=True)
    else:
        logger.info(
            "Backend starting in %s — skipping strict env validation.",
            settings.APP_ENV,
        )

    logger.info("Backend starting — ensuring campus navigation data is ready.")
    ensure_navigation_data_ready()

    logger.info("Backend starting — launching sensor ingestion scheduler.")
    task = asyncio.create_task(run_sensor_ingestion_loop())
    yield
    logger.info("Backend shutting down — stopping sensor ingestion scheduler.")
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    logger.info("Sensor ingestion scheduler stopped.")


app = FastAPI(title="Campus-Aware Intelligent AI Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(sensor.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "port": settings.APP_PORT,
    }


if rag_router is not None:
    app.include_router(rag_router, prefix="/rag", tags=["RAG"])
