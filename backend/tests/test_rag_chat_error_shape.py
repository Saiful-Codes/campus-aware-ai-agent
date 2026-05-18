import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app


def _noop():
    async def _runner():
        pass

    return _runner


def test_rag_chat_success_returns_answer_without_error_flag():
    async def noop():
        pass

    with patch("app.main.run_sensor_ingestion_loop", new=noop), patch(
        "app.api.rag_chat.generate_answer", return_value="Hello from RAG."
    ):
        with TestClient(app) as client:
            response = client.post("/rag/chat", json={"message": "hi"})

    assert response.status_code == 200
    body = response.json()
    assert body == {"response": "Hello from RAG."}


def test_rag_chat_failure_returns_null_response_with_error_flag():
    async def noop():
        pass

    def boom(_question):
        raise RuntimeError("simulated downstream failure")

    with patch("app.main.run_sensor_ingestion_loop", new=noop), patch(
        "app.api.rag_chat.generate_answer", side_effect=boom
    ):
        with TestClient(app) as client:
            response = client.post("/rag/chat", json={"message": "trigger error"})

    assert response.status_code == 200
    body = response.json()
    # Mobile fallback chain relies on response being null/falsy to fall through to /chat.
    assert body["response"] is None
    # New error flag is what callers/log inspectors can branch on.
    assert body["error"] is True


def test_rag_chat_failure_tolerates_extra_request_fields():
    """Mobile sends user_id and chat_id alongside message; the endpoint must
    accept these without 422 even though the schema only declares 'message'."""
    async def noop():
        pass

    with patch("app.main.run_sensor_ingestion_loop", new=noop), patch(
        "app.api.rag_chat.generate_answer", return_value="ok"
    ):
        with TestClient(app) as client:
            response = client.post(
                "/rag/chat",
                json={"message": "hi", "user_id": "u1", "chat_id": "c1"},
            )

    assert response.status_code == 200
    assert response.json() == {"response": "ok"}
