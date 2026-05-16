import importlib
import os
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def _isolate_pg_db_env():
    """Snapshot/restore POSTGRES_/DB_ env vars around each test.

    Settings._alias_postgres_env() writes directly to os.environ, which
    bypasses pytest's monkeypatch tracking. Without this fixture, a test
    that sets POSTGRES_* would leak DB_* values into later tests.
    """
    keys = (
        "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD",
        "POSTGRES_HOST", "POSTGRES_PORT",
        "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT",
    )
    snapshot = {k: os.environ.get(k) for k in keys}
    try:
        yield
    finally:
        for k, v in snapshot.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


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


def test_postgres_env_aliased_to_db_underscore_for_rag(monkeypatch):
    """If only POSTGRES_* are set, DB_* must also be available in os.environ
    because the RAG pipeline reads DB_* directly via os.getenv().
    """
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    monkeypatch.setenv("POSTGRES_DB", "alpha")
    monkeypatch.setenv("POSTGRES_USER", "beta")
    monkeypatch.setenv("POSTGRES_PASSWORD", "gamma")
    monkeypatch.setenv("POSTGRES_HOST", "h")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)

    import os

    _reload_config()

    assert os.environ.get("DB_NAME") == "alpha"
    assert os.environ.get("DB_USER") == "beta"
    assert os.environ.get("DB_PASSWORD") == "gamma"
    assert os.environ.get("DB_HOST") == "h"
    assert os.environ.get("DB_PORT") == "5433"


def test_db_underscore_env_aliased_to_postgres(monkeypatch):
    """If only DB_* are set, POSTGRES_* must also be available so the Settings
    class and any POSTGRES_*-based consumer keep working.
    """
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    monkeypatch.delenv("POSTGRES_PORT", raising=False)
    monkeypatch.setenv("DB_NAME", "alpha")
    monkeypatch.setenv("DB_USER", "beta")
    monkeypatch.setenv("DB_PASSWORD", "gamma")

    import os

    _reload_config()

    assert os.environ.get("POSTGRES_DB") == "alpha"
    assert os.environ.get("POSTGRES_USER") == "beta"
    assert os.environ.get("POSTGRES_PASSWORD") == "gamma"


def test_alias_does_not_overwrite_when_both_sets_present(monkeypatch):
    """If both sets are set (with different values), neither is overwritten."""
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)

    monkeypatch.setenv("POSTGRES_DB", "from_postgres")
    monkeypatch.setenv("DB_NAME", "from_db")
    monkeypatch.setenv("POSTGRES_USER", "u1")
    monkeypatch.setenv("DB_USER", "u2")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p1")
    monkeypatch.setenv("DB_PASSWORD", "p2")

    import os

    _reload_config()

    assert os.environ["POSTGRES_DB"] == "from_postgres"
    assert os.environ["DB_NAME"] == "from_db"
    assert os.environ["POSTGRES_USER"] == "u1"
    assert os.environ["DB_USER"] == "u2"


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
