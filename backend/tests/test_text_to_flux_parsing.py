import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.text_to_flux_service import (
    _parse_record_values,
    clean_flux_output,
    get_time_range_info,
    _build_no_data_message,
)


# ---------------------------------------------------------------------------
# _parse_record_values — pure record-parsing helper
# ---------------------------------------------------------------------------

def test_parse_skips_record_with_none_value():
    result = _parse_record_values({"_field": "temperature"}, None, None)
    assert result is None


def test_parse_keeps_valid_temperature_record():
    result = _parse_record_values({"_field": "temperature"}, 21.5, None)
    assert result == {"time": None, "field": "temperature", "value": 21.5}


def test_parse_keeps_valid_humidity_record():
    result = _parse_record_values({"_field": "humidity"}, 65.0, None)
    assert result == {"time": None, "field": "humidity", "value": 65.0}


def test_parse_rounds_float_to_two_decimal_places():
    result = _parse_record_values({"_field": "humidity"}, 65.5555, None)
    assert result is not None
    assert result["value"] == 65.56


def test_parse_skips_metadata_field_named_time():
    # _time appearing as _field is metadata noise, not a sensor reading
    result = _parse_record_values({"_field": "_time"}, "2026-04-08", None)
    assert result is None


def test_parse_skips_measurement_as_field():
    result = _parse_record_values({"_field": "_measurement"}, "sensor_readings", None)
    assert result is None


def test_parse_skips_unsupported_field_name():
    result = _parse_record_values({"_field": "unknown_sensor"}, 42.0, None)
    assert result is None


def test_parse_uses_none_time_when_raw_time_is_none():
    result = _parse_record_values({"_field": "pressure"}, 1013.2, None)
    assert result is not None
    assert result["time"] is None


def test_parse_stringifies_datetime_time():
    t = datetime(2026, 4, 8, 16, 0, 0, tzinfo=timezone.utc)
    result = _parse_record_values({"_field": "temperature"}, 21.5, t)
    assert result is not None
    assert result["time"] is not None
    assert "2026" in result["time"]


def test_parse_infers_field_from_pivot_result():
    # pivot() removes _field column; sensor field name becomes a column key
    values = {"temperature": 21.5, "_measurement": "sensor_readings"}
    result = _parse_record_values(values, None, None)
    assert result is not None
    assert result["field"] == "temperature"
    assert result["value"] == 21.5


def test_parse_pivot_result_rounds_value():
    values = {"humidity": 63.9999, "_measurement": "sensor_readings"}
    result = _parse_record_values(values, None, None)
    assert result is not None
    assert result["value"] == 64.0


def test_parse_skips_pivot_record_with_no_sensor_columns():
    # Pivot record with only metadata columns — nothing useful to extract
    values = {"_measurement": "sensor_readings", "_start": "2026-01-01"}
    result = _parse_record_values(values, None, None)
    assert result is None


# ---------------------------------------------------------------------------
# clean_flux_output — existing pure helper, regression + edge cases
# ---------------------------------------------------------------------------

def test_clean_flux_output_strips_flux_fence():
    raw = "```flux\nfrom(bucket: \"test\") |> range(start: -7d)\n```"
    result = clean_flux_output(raw)
    assert "```" not in result


def test_clean_flux_output_strips_generic_fence():
    raw = "```\nfrom(bucket: \"test\") |> range(start: -7d)\n```"
    result = clean_flux_output(raw)
    assert "```" not in result


def test_clean_flux_output_appends_limit_for_raw_query():
    raw = 'from(bucket: "test") |> range(start: -7d) |> filter(fn: (r) => r._field == "temperature")'
    result = clean_flux_output(raw)
    assert "limit(n: 20)" in result


def test_clean_flux_output_skips_limit_when_mean_present():
    raw = 'from(bucket: "test") |> range(start: -7d) |> mean()'
    result = clean_flux_output(raw)
    assert result.count("limit") == 0


def test_clean_flux_output_skips_limit_when_max_present():
    raw = 'from(bucket: "test") |> range(start: -7d) |> max()'
    result = clean_flux_output(raw)
    assert result.count("limit") == 0


def test_clean_flux_output_skips_limit_when_aggregatewindow_present():
    raw = 'from(bucket: "test") |> range(start: -7d) |> aggregateWindow(every: 1h, fn: mean)'
    result = clean_flux_output(raw)
    assert result.count("limit") == 0


def test_clean_flux_output_does_not_double_limit():
    raw = 'from(bucket: "test") |> range(start: -7d) |> limit(n: 10)'
    result = clean_flux_output(raw)
    assert result.count("limit") == 1


# ---------------------------------------------------------------------------
# get_time_range_info — natural language → Flux range + human label
# ---------------------------------------------------------------------------

def test_time_range_info_this_week():
    info = get_time_range_info("Show temperature trend over time this week")
    assert info["flux_range"] == "start: -7d"
    assert info["label"] == "this week"


def test_time_range_info_last_week():
    info = get_time_range_info("What was the temperature last week?")
    assert info["flux_range"] == "start: -14d"
    assert info["label"] == "last week"


def test_time_range_info_today():
    info = get_time_range_info("Show temperature readings from today")
    assert info["flux_range"] == "start: -24h"
    assert info["label"] == "today"


def test_time_range_info_yesterday():
    info = get_time_range_info("What was the humidity yesterday?")
    assert info["flux_range"] == "start: -48h"
    assert info["label"] == "yesterday"


def test_time_range_info_this_month():
    info = get_time_range_info("Show temperature trend this month")
    assert info["flux_range"] == "start: -30d"
    assert info["label"] == "this month"


def test_time_range_info_last_month():
    info = get_time_range_info("Show humidity readings from last month")
    assert info["flux_range"] == "start: -60d"
    assert info["label"] == "last month"


def test_time_range_info_last_hour():
    info = get_time_range_info("Show temperature from the last hour")
    assert info["flux_range"] == "start: -1h"
    assert info["label"] == "the last hour"


def test_time_range_info_this_year():
    info = get_time_range_info("Show temperature trend this year")
    assert info["flux_range"] == "start: -365d"
    assert info["label"] == "this year"


def test_time_range_info_april_2026():
    info = get_time_range_info("What was the temperature in April 2026?")
    assert "2026-04-01T00:00:00Z" in info["flux_range"]
    assert "2026-05-01T00:00:00Z" in info["flux_range"]
    assert info["label"] == "April 2026"


def test_time_range_info_march_2025():
    info = get_time_range_info("Show humidity readings from March 2025")
    assert "2025-03-01T00:00:00Z" in info["flux_range"]
    assert "2025-04-01T00:00:00Z" in info["flux_range"]
    assert info["label"] == "March 2025"


def test_time_range_info_december_wraps_to_january():
    info = get_time_range_info("Show temperature in December 2024")
    assert "2024-12-01T00:00:00Z" in info["flux_range"]
    assert "2025-01-01T00:00:00Z" in info["flux_range"]
    assert info["label"] == "December 2024"


def test_time_range_info_year_only_1995():
    info = get_time_range_info("What was the humidity in 1995?")
    assert "1995-01-01T00:00:00Z" in info["flux_range"]
    assert "1996-01-01T00:00:00Z" in info["flux_range"]
    assert info["label"] == "1995"


def test_time_range_info_year_only_2024():
    info = get_time_range_info("Show all temperature readings from 2024")
    assert "2024-01-01T00:00:00Z" in info["flux_range"]
    assert "2025-01-01T00:00:00Z" in info["flux_range"]
    assert info["label"] == "2024"


def test_time_range_info_defaults_when_no_time_keyword():
    info = get_time_range_info("Show all temperature readings")
    assert info["flux_range"] == "start: -30d"
    assert "30" in info["label"]


# ---------------------------------------------------------------------------
# _build_no_data_message — contextual no-data response
# ---------------------------------------------------------------------------

def test_no_data_message_includes_label():
    msg = _build_no_data_message("this week")
    assert "this week" in msg


def test_no_data_message_includes_time_range_hint():
    msg = _build_no_data_message("April 2026")
    assert "April 2026" in msg
    assert "time range" in msg.lower() or "readings" in msg.lower()


def test_no_data_message_for_year_label():
    msg = _build_no_data_message("1995")
    assert "1995" in msg


# ---------------------------------------------------------------------------
# Sprint 5: time_label threading into format_flux_result
# ---------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

import app.services.text_to_flux_service as t2f


def test_format_flux_result_passes_time_label_into_prompt():
    captured_prompts = []

    fake_response = MagicMock()
    fake_response.text = "It was warm."

    def fake_generate(*args, **kwargs):
        captured_prompts.append(kwargs.get("contents", ""))
        return fake_response

    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = fake_generate

    with patch.object(t2f, "client", fake_client):
        t2f.format_flux_result(
            user_question="What was the temperature yesterday?",
            flux_query="from(bucket: \"x\")",
            query_result=[{"time": None, "field": "temperature", "value": 22.0}],
            time_label="yesterday",
        )

    assert any("yesterday" in p for p in captured_prompts)


def test_format_flux_result_default_time_label_is_safe():
    fake_response = MagicMock()
    fake_response.text = "ok"

    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = fake_response

    with patch.object(t2f, "client", fake_client):
        # Backward compatibility: omitting time_label must not raise.
        result = t2f.format_flux_result(
            "q",
            "flux",
            [{"time": None, "field": "temperature", "value": 22.0}],
        )

    assert result == "ok"


def test_answer_sensor_flux_question_forwards_time_label():
    captured_prompts = []

    fake_response = MagicMock()
    fake_response.text = "trend looks stable"

    def fake_generate(*args, **kwargs):
        captured_prompts.append(kwargs.get("contents", ""))
        return fake_response

    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = fake_generate

    with patch.object(t2f, "client", fake_client), \
         patch.object(t2f, "generate_flux_from_question", return_value=(
             'from(bucket: "sensor_data") |> range(start: -48h) '
             '|> filter(fn: (r) => r["_measurement"] == "sensor_readings") '
             '|> filter(fn: (r) => r["_field"] == "temperature") |> mean()'
         )), \
         patch.object(t2f, "run_flux_query", return_value=[
             {"time": None, "field": "temperature", "value": 22.0}
         ]):
        t2f.answer_sensor_flux_question("What was the temperature yesterday?")

    # The formatter prompt must mention "yesterday".
    assert any("yesterday" in p for p in captured_prompts)
