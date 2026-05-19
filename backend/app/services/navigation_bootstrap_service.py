import logging
from pathlib import Path
from typing import Tuple

import psycopg2

from app.core.config import settings
from app.services.postgres_service import open_postgres_connection


logger = logging.getLogger(__name__)


def _open_pg_connection():
    return open_postgres_connection()


def _bootstrap_sql_path() -> Path:
    return Path(__file__).resolve().parents[1] / "db" / "campus_navigation_bootstrap.sql"


def bootstrap_navigation_data() -> Tuple[int, int, int]:
    sql_path = _bootstrap_sql_path()
    if not sql_path.exists():
        raise FileNotFoundError(f"Navigation bootstrap SQL not found: {sql_path}")

    sql = sql_path.read_text(encoding="utf-8")

    conn = _open_pg_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
        conn.commit()

        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM locations;")
            locations_count = int(cursor.fetchone()[0])
            cursor.execute("SELECT COUNT(*) FROM facilities;")
            facilities_count = int(cursor.fetchone()[0])
            cursor.execute("SELECT COUNT(*) FROM paths;")
            paths_count = int(cursor.fetchone()[0])
    finally:
        conn.close()

    return locations_count, facilities_count, paths_count


def ensure_navigation_data_ready() -> None:
    try:
        locations_count, facilities_count, paths_count = bootstrap_navigation_data()
        logger.info(
            "Navigation data ready: %s locations, %s facilities, %s paths",
            locations_count,
            facilities_count,
            paths_count,
        )
    except Exception as exc:
        logger.warning("Navigation bootstrap skipped or failed: %s", exc)
