import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

import app.services.llm_service as llm

# --- Exact fallback strings the spec freezes ---

BUSY_MESSAGE = "Sorry, the AI service is busy right now. Please try again in a moment."
EMPTY_RESPONSE_MESSAGE = (
    "I couldn't generate a reliable answer for that question. "
    "Please try rephrasing or simplifying your request."
)


# ---------------------------------------------------------------------------
# generate_response
# ---------------------------------------------------------------------------

def test_generate_response_returns_text_and_success_on_helper_success():
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        return_value="answer body",
    ):
        text, status = llm.generate_response("hi")

    assert text == "answer body"
    assert status == "success"


def test_generate_response_returns_exact_busy_message_on_GeminiCallError():
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        side_effect=llm.GeminiCallError("boom"),
    ):
        text, status = llm.generate_response("hi")

    assert text == BUSY_MESSAGE
    assert status == "error"


def test_generate_response_returns_exact_empty_message_when_helper_returns_empty():
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        return_value="",
    ):
        text, status = llm.generate_response("hi")

    assert text == EMPTY_RESPONSE_MESSAGE
    assert status == "error"


# ---------------------------------------------------------------------------
# generate_sensor_response
# ---------------------------------------------------------------------------

def test_generate_sensor_response_preserves_sensor_no_data_early_return():
    text, status = llm.generate_sensor_response("hi", None)
    assert status == "sensor_no_data"
    assert text == "No recent sensor data is available at the moment. Please try again shortly."


def test_generate_sensor_response_returns_text_and_status_on_helper_success():
    sensor_data = {
        "temperature": 22.0,
        "humidity": 55.0,
        "pressure": 1013.2,
        "dew_point": 12.5,
        "timestamp": "2026-05-17T10:00:00Z",
    }
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        return_value="It is 22 degrees.",
    ):
        text, status = llm.generate_sensor_response("temperature?", sensor_data)

    assert text == "It is 22 degrees."
    assert status == "sensor_response"


def test_generate_sensor_response_returns_exact_busy_message_on_GeminiCallError():
    sensor_data = {"temperature": 22.0}
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        side_effect=llm.GeminiCallError("boom"),
    ):
        text, status = llm.generate_sensor_response("temperature?", sensor_data)

    assert text == BUSY_MESSAGE
    assert status == "error"


def test_generate_sensor_response_returns_exact_empty_message_when_helper_returns_empty():
    sensor_data = {"temperature": 22.0}
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        return_value="",
    ):
        text, status = llm.generate_sensor_response("temperature?", sensor_data)

    assert text == EMPTY_RESPONSE_MESSAGE
    assert status == "error"


# ---------------------------------------------------------------------------
# generate_hybrid_response
# ---------------------------------------------------------------------------

def test_generate_hybrid_response_returns_text_and_status_on_helper_success():
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        return_value="hybrid body",
    ):
        text, status = llm.generate_hybrid_response("hi", ["chunk one"])

    assert text == "hybrid body"
    assert status == "hybrid_response"


def test_generate_hybrid_response_returns_exact_busy_message_on_GeminiCallError():
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        side_effect=llm.GeminiCallError("boom"),
    ):
        text, status = llm.generate_hybrid_response("hi", ["chunk one"])

    assert text == BUSY_MESSAGE
    assert status == "error"


def test_generate_hybrid_response_returns_exact_empty_message_when_helper_returns_empty():
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        return_value="",
    ):
        text, status = llm.generate_hybrid_response("hi", ["chunk one"])

    assert text == EMPTY_RESPONSE_MESSAGE
    assert status == "error"


def test_generate_hybrid_response_handles_empty_context_chunks():
    with patch(
        "app.services.llm_service.call_gemini_with_retry",
        return_value="hybrid body",
    ):
        text, status = llm.generate_hybrid_response("hi", [])

    assert text == "hybrid body"
    assert status == "hybrid_response"
