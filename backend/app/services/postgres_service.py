from typing import Optional

import psycopg2

from app.core.config import settings


def open_postgres_connection() -> psycopg2.extensions.connection:
    """Open PostgreSQL connection using configured env values, with dev fallback.

    Fallback only helps local development if the configured host/port is stale.
    """
    candidates = [
        {
            "dbname": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
        }
    ]

    docker_default = {
        "dbname": "campus_ai",
        "user": "postgres",
        "password": "postgres",
        "host": "127.0.0.1",
        "port": 5432,
    }

    if (
        settings.APP_ENV == "development"
        and (
            settings.POSTGRES_DB != docker_default["dbname"]
            or settings.POSTGRES_USER != docker_default["user"]
            or settings.POSTGRES_PASSWORD != docker_default["password"]
            or str(settings.POSTGRES_HOST) != docker_default["host"]
            or int(settings.POSTGRES_PORT) != docker_default["port"]
        )
    ):
        candidates.append(docker_default)

    last_error: Optional[Exception] = None
    for params in candidates:
        try:
            return psycopg2.connect(connect_timeout=3, **params)
        except Exception as exc:
            last_error = exc

    assert last_error is not None
    raise last_error
