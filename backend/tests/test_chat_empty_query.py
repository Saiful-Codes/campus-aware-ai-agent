import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app


def _noop_scheduler():
    async def noop():
        pass
    return patch("app.main.run_sensor_ingestion_loop", new=noop)


def test_empty_query_returns_empty_query_status_without_calling_gemini():
    with _noop_scheduler():
        with patch("app.api.chat.classify_query_intent") as mock_classify:
            with TestClient(app) as client:
                response = client.post("/chat", json={"query": ""})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "empty_query"
    assert "please" in body["answer"].lower()
    mock_classify.assert_not_called()


def test_whitespace_only_query_returns_empty_query_status():
    with _noop_scheduler():
        with patch("app.api.chat.classify_query_intent") as mock_classify:
            with TestClient(app) as client:
                response = client.post("/chat", json={"query": "   \t\n  "})

    assert response.status_code == 200
    assert response.json()["status"] == "empty_query"
    mock_classify.assert_not_called()


def test_non_empty_query_still_calls_classify_intent():
    with _noop_scheduler():
        with patch("app.api.chat.classify_query_intent") as mock_classify:
            mock_classify.return_value = {
                "intent": "normal_llm",
                "confidence": 0.7,
                "requiredTools": ["llm"],
                "reason": "test",
            }
            with patch(
                "app.api.chat.generate_response",
                return_value=("ok", "success"),
            ):
                with TestClient(app) as client:
                    response = client.post("/chat", json={"query": "Hello"})

    assert response.status_code == 200
    mock_classify.assert_called_once()
