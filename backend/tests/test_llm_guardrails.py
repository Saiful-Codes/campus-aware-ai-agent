import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.llm_service import generate_sensor_response


# ---------------------------------------------------------------------------
# generate_sensor_response — null guard
# These tests must NOT call the Gemini API (early return before any API call).
# ---------------------------------------------------------------------------

def test_sensor_response_handles_none_sensor_data():
    answer, status = generate_sensor_response("What is the current temperature?", None)
    assert isinstance(answer, str)
    assert len(answer) > 0
    assert status == "sensor_no_data"


def test_sensor_response_handles_empty_dict_sensor_data():
    answer, status = generate_sensor_response("What is the humidity right now?", {})
    assert isinstance(answer, str)
    assert len(answer) > 0
    assert status == "sensor_no_data"


def test_sensor_response_none_answer_mentions_unavailability():
    answer, _ = generate_sensor_response("What is the pressure?", None)
    lower = answer.lower()
    assert "no" in lower or "not available" in lower or "unavailable" in lower


def test_sensor_response_empty_dict_does_not_crash():
    try:
        generate_sensor_response("Tell me about the sensor conditions.", {})
    except (AttributeError, TypeError) as e:
        raise AssertionError(f"generate_sensor_response crashed with empty dict: {e}")
