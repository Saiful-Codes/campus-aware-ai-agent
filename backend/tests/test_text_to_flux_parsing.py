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


# ---------------------------------------------------------------------------
# Sprint 5: human-readable record formatting helper
# ---------------------------------------------------------------------------

from app.services.text_to_flux_service import _format_records_for_prompt


def test_format_records_single_temperature_with_time():
    out = _format_records_for_prompt([
        {"time": "2026-05-15T10:00:00Z", "field": "temperature", "value": 22.3}
    ])
    assert "temperature: 22.3 °C" in out
    assert "at 2026-05-15T10:00:00Z" in out


def test_format_records_humidity_units():
    out = _format_records_for_prompt([
        {"time": None, "field": "humidity", "value": 58.0}
    ])
    assert "humidity: 58.0 %" in out
    assert "at " not in out


def test_format_records_pressure_units():
    out = _format_records_for_prompt([
        {"time": None, "field": "pressure", "value": 1013.2}
    ])
    assert "pressure: 1013.2 hPa" in out


def test_format_records_dew_point_units():
    out = _format_records_for_prompt([
        {"time": None, "field": "dew_point", "value": 12.5}
    ])
    assert "dew_point: 12.5 °C" in out


def test_format_records_multiple_lines():
    out = _format_records_for_prompt([
        {"time": None, "field": "temperature", "value": 22.0},
        {"time": None, "field": "temperature", "value": 23.5},
    ])
    lines = [line for line in out.splitlines() if line.strip()]
    assert len(lines) == 2


def test_format_records_unknown_field_uses_no_unit():
    out = _format_records_for_prompt([
        {"time": None, "field": "mystery", "value": 7.0}
    ])
    # Should still produce a sensible line, just without a unit suffix.
    assert "mystery: 7.0" in out
    assert "°C" not in out


def test_format_records_empty_list_returns_empty_string():
    assert _format_records_for_prompt([]) == ""


# ---------------------------------------------------------------------------
# Sprint 5 Batch C: field-aware no-data messaging (#23)
# ---------------------------------------------------------------------------

from app.services.text_to_flux_service import _detect_sensor_field


def test_detect_sensor_field_temperature():
    assert _detect_sensor_field("What was the temperature yesterday?") == "temperature"


def test_detect_sensor_field_humidity():
    assert _detect_sensor_field("Show humidity readings") == "humidity"


def test_detect_sensor_field_pressure():
    assert _detect_sensor_field("What is the average pressure?") == "pressure"


def test_detect_sensor_field_dew_point():
    assert _detect_sensor_field("Dew point trend over last week") == "dew_point"


def test_detect_sensor_field_returns_none_when_no_field_mentioned():
    assert _detect_sensor_field("How was the weather?") is None


def test_detect_sensor_field_returns_none_when_multiple_fields_mentioned():
    assert _detect_sensor_field("Compare temperature and humidity") is None


def test_no_data_message_generic_when_field_label_is_none():
    # Regression: generic message remains byte-identical for the no-field branch.
    msg = _build_no_data_message("this week")
    assert msg == (
        "No matching sensor data was found for this week. "
        "The database may not contain readings for that time range."
    )


def test_no_data_message_field_aware_temperature():
    msg = _build_no_data_message("yesterday", field_label="temperature")
    assert "temperature" in msg
    assert "yesterday" in msg


def test_no_data_message_field_aware_dew_point_uses_human_label():
    msg = _build_no_data_message("April 2026", field_label="dew_point")
    # dew_point should render as "dew point" in user-facing text.
    assert "dew point" in msg
    assert "dew_point" not in msg


# ---------------------------------------------------------------------------
# Sprint 5: aggregate record parsing — group() |> mean() drops _field and _time
# ---------------------------------------------------------------------------

def test_parse_aggregate_record_with_fallback_field_uses_it():
    # After group() |> mean(), record.values lacks _field and _time
    values = {"result": "_result", "table": 0, "_start": "x", "_stop": "y", "_value": 94.74}
    result = _parse_record_values(values, 94.74, None, fallback_field="humidity")
    assert result is not None
    assert result["field"] == "humidity"
    assert result["value"] == 94.74
    assert result["time"] is None


def test_parse_aggregate_record_without_fallback_field_returns_none():
    values = {"result": "_result", "table": 0, "_start": "x", "_stop": "y", "_value": 94.74}
    result = _parse_record_values(values, 94.74, None)
    assert result is None


def test_parse_aggregate_record_with_invalid_fallback_field_returns_none():
    values = {"result": "_result", "table": 0, "_start": "x", "_stop": "y", "_value": 94.74}
    result = _parse_record_values(values, 94.74, None, fallback_field="not_a_sensor")
    assert result is None


def test_parse_aggregate_record_rounds_float_with_fallback():
    values = {"_value": 94.7417543859649}
    result = _parse_record_values(values, 94.7417543859649, None, fallback_field="humidity")
    assert result is not None
    assert result["value"] == 94.74


def test_parse_explicit_field_wins_over_fallback():
    # When _field is present and valid, fallback_field must not override it.
    result = _parse_record_values(
        {"_field": "temperature"}, 21.5, None, fallback_field="humidity"
    )
    assert result == {"time": None, "field": "temperature", "value": 21.5}


# ---------------------------------------------------------------------------
# Sprint 5: run_flux_query — aggregate records (missing _time) must survive
# ---------------------------------------------------------------------------

from app.services.text_to_flux_service import run_flux_query


def _fake_influx_client(records):
    """Build a stand-in Influx client whose query_api().query() yields records.

    Each record is a MagicMock configured with .values, .get_value(), .get_time().
    """
    fake_records = []
    for r in records:
        mock_rec = MagicMock()
        mock_rec.values = r["values"]
        if "value_raises" in r:
            mock_rec.get_value.side_effect = r["value_raises"]
        else:
            mock_rec.get_value.return_value = r["value"]
        if "time_raises" in r:
            mock_rec.get_time.side_effect = r["time_raises"]
        else:
            mock_rec.get_time.return_value = r.get("time")
        fake_records.append(mock_rec)

    fake_table = MagicMock()
    fake_table.records = fake_records

    fake_client = MagicMock()
    fake_client.query_api.return_value.query.return_value = [fake_table]
    return fake_client


def test_run_flux_query_aggregate_record_missing_time_is_parsed():
    fake_client = _fake_influx_client([
        {
            "values": {"result": "_result", "table": 0, "_value": 94.74},
            "value": 94.74,
            "time_raises": KeyError("_time"),
        }
    ])

    with patch.object(t2f, "get_influx_client", return_value=fake_client):
        result = t2f.run_flux_query("from(bucket: \"x\")", fallback_field="humidity")

    assert len(result) == 1
    assert result[0]["field"] == "humidity"
    assert result[0]["value"] == 94.74
    assert result[0]["time"] is None


def test_run_flux_query_normal_raw_record_still_parses():
    fake_client = _fake_influx_client([
        {
            "values": {"_field": "temperature", "_value": 21.5},
            "value": 21.5,
            "time": datetime(2026, 5, 17, 14, 23, 57, tzinfo=timezone.utc),
        }
    ])

    with patch.object(t2f, "get_influx_client", return_value=fake_client):
        result = t2f.run_flux_query("from(bucket: \"x\")")

    assert len(result) == 1
    assert result[0]["field"] == "temperature"
    assert result[0]["value"] == 21.5
    assert "2026" in result[0]["time"]


def test_run_flux_query_skips_record_when_get_value_raises():
    fake_client = _fake_influx_client([
        {
            "values": {"_field": "temperature"},
            "value_raises": KeyError("_value"),
        }
    ])

    with patch.object(t2f, "get_influx_client", return_value=fake_client):
        result = t2f.run_flux_query("from(bucket: \"x\")", fallback_field="temperature")

    assert result == []


def test_answer_sensor_flux_question_aggregate_humidity_returns_data():
    """Integration-style: aggregate Flux returns a single record with no _time/_field;
    answer_sensor_flux_question must pass detected field as fallback and produce data."""

    fake_response = MagicMock()
    fake_response.text = "Average humidity was about 94.74%."
    fake_llm_client = MagicMock()
    fake_llm_client.models.generate_content.return_value = fake_response

    fake_influx = _fake_influx_client([
        {
            "values": {"result": "_result", "table": 0, "_value": 94.74},
            "value": 94.74,
            "time_raises": KeyError("_time"),
        }
    ])

    flux = (
        'from(bucket: "sensor_data") |> range(start: -7d) '
        '|> filter(fn: (r) => r["_measurement"] == "sensor_readings") '
        '|> filter(fn: (r) => r["_field"] == "humidity") '
        '|> group() |> mean()'
    )

    with patch.object(t2f, "client", fake_llm_client), \
         patch.object(t2f, "generate_flux_from_question", return_value=flux), \
         patch.object(t2f, "get_influx_client", return_value=fake_influx), \
         patch.object(t2f, "INFLUX_BUCKET", "sensor_data"):
        result = t2f.answer_sensor_flux_question(
            "What was the average humidity in the last 7 days?"
        )

    assert result["status"] == "text_to_flux_response"
    assert len(result["data"]) == 1
    assert result["data"][0]["field"] == "humidity"
    assert result["data"][0]["value"] == 94.74


# ---------------------------------------------------------------------------
# Sprint 5: "last N <unit>" / "past N <unit>" time-range parsing
# ---------------------------------------------------------------------------

def test_time_range_info_last_7_days():
    info = get_time_range_info("What was the average humidity in the last 7 days?")
    assert info["flux_range"] == "start: -7d"
    assert info["label"] == "the last 7 days"


def test_time_range_info_past_7_days():
    info = get_time_range_info("Show humidity from the past 7 days")
    assert info["flux_range"] == "start: -7d"
    assert info["label"] == "the past 7 days"


def test_time_range_info_last_14_days():
    info = get_time_range_info("Show temperature trend over the last 14 days")
    assert info["flux_range"] == "start: -14d"
    assert info["label"] == "the last 14 days"


def test_time_range_info_last_3_weeks():
    info = get_time_range_info("Show temperature over the last 3 weeks")
    assert info["flux_range"] == "start: -21d"
    assert info["label"] == "the last 3 weeks"


def test_time_range_info_last_6_hours():
    info = get_time_range_info("Show humidity from the last 6 hours")
    assert info["flux_range"] == "start: -6h"
    assert info["label"] == "the last 6 hours"


def test_time_range_info_last_week_regression_still_explicit():
    # Regression: the explicit "last week" branch must keep mapping to -14d / "last week"
    # (NOT "last 1 weeks" or similar from a numeric fallthrough).
    info = get_time_range_info("What was the temperature last week?")
    assert info["flux_range"] == "start: -14d"
    assert info["label"] == "last week"
