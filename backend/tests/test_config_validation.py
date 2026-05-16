import importlib
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))


def _reload_config():
    import app.core.config as config_module
    importlib.reload(config_module)
    return config_module


def test_validate_required_returns_missing_when_gemini_key_absent(monkeypatch):
    import dotenv

    # Stub out load_dotenv so backend/.env doesn't re-supply GEMINI_API_KEY
    # during the config reload below.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("INFLUXDB_URL", "http://localhost:18086")
    monkeypatch.setenv("INFLUXDB_TOKEN", "x")
    monkeypatch.setenv("INFLUXDB_ORG", "x")
    monkeypatch.setenv("INFLUXDB_BUCKET", "x")
    monkeypatch.setenv("POSTGRES_DB", "x")
    monkeypatch.setenv("POSTGRES_USER", "x")
    monkeypatch.setenv("POSTGRES_PASSWORD", "x")

    config = _reload_config()
    missing = config.settings.validate_required(strict=False)

    assert "GEMINI_API_KEY" in missing


def test_validate_required_accepts_db_underscore_convention(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    monkeypatch.setenv("INFLUXDB_URL", "http://localhost:18086")
    monkeypatch.setenv("INFLUXDB_TOKEN", "x")
    monkeypatch.setenv("INFLUXDB_ORG", "x")
    monkeypatch.setenv("INFLUXDB_BUCKET", "x")
    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.setenv("DB_NAME", "x")
    monkeypatch.setenv("DB_USER", "x")
    monkeypatch.setenv("DB_PASSWORD", "x")

    config = _reload_config()
    missing = config.settings.validate_required(strict=False)

    assert missing == []


def test_validate_required_raises_when_strict_and_missing(monkeypatch):
    import dotenv

    # Block .env from re-supplying values during the reload below.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("INFLUXDB_URL", raising=False)
    monkeypatch.delenv("INFLUXDB_TOKEN", raising=False)
    monkeypatch.delenv("INFLUXDB_ORG", raising=False)
    monkeypatch.delenv("INFLUXDB_BUCKET", raising=False)
    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)

    config = _reload_config()

    with pytest.raises(RuntimeError) as exc_info:
        config.settings.validate_required(strict=True)

    msg = str(exc_info.value)
    assert "GEMINI_API_KEY" in msg
    assert "INFLUXDB" in msg


def test_lifespan_skips_validation_in_development(monkeypatch):
    # Smoke test: TestClient startup must not raise when APP_ENV defaults
    # to "development" and required vars happen to be missing in CI.
    from unittest.mock import patch
    from fastapi.testclient import TestClient

    monkeypatch.setenv("APP_ENV", "development")

    async def noop():
        pass

    from app.main import app

    with patch("app.main.run_sensor_ingestion_loop", new=noop):
        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
