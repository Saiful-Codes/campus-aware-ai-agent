import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app


def test_health_check():
    async def noop():
        pass

    with patch("app.main.run_sensor_ingestion_loop", new=noop):
        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
