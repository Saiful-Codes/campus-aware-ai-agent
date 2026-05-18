import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app


def test_chat_accepts_query_at_max_length_boundary():
    async def noop():
        pass

    with patch("app.main.run_sensor_ingestion_loop", new=noop):
        with TestClient(app) as client:
            response = client.post("/chat", json={"query": "x" * 2000})

    # Boundary-valid query reaches normal processing; exact status depends on
    # routing, but it MUST NOT be 422.
    assert response.status_code != 422


def test_chat_rejects_query_above_max_length():
    async def noop():
        pass

    with patch("app.main.run_sensor_ingestion_loop", new=noop):
        with TestClient(app) as client:
            response = client.post("/chat", json={"query": "x" * 2001})

    assert response.status_code == 422


def test_chat_still_accepts_empty_query_with_empty_query_status():
    # Regression: Batch A #21 empty-query short-circuit must continue to work.
    # max_length only adds an upper bound; no min_length was added.
    async def noop():
        pass

    with patch("app.main.run_sensor_ingestion_loop", new=noop):
        with TestClient(app) as client:
            response = client.post("/chat", json={"query": ""})

    assert response.status_code == 200
    assert response.json()["status"] == "empty_query"
