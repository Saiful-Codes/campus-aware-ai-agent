import os
from pathlib import Path
from dotenv import load_dotenv

# Build absolute path to backend/.env
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

# Explicitly load backend/.env
load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", 8000))

    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "campus_ai")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

    INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "")
    INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "")
    INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


settings = Settings()
