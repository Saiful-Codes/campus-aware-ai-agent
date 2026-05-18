from app.services.text_to_flux_service import is_safe_flux_query
from unittest.mock import MagicMock, patch
from app.services.text_to_flux_service import (
    answer_sensor_flux_question,
    run_flux_query,
)



VALID_QUERY = """
from(bucket: "sensor_data")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> mean()
"""


def test_blocks_empty_query():
    assert is_safe_flux_query("") is False


def test_blocks_wrong_bucket():
    query = """
    from(bucket: "wrong_bucket")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
    """
    assert is_safe_flux_query(query) is False


def test_blocks_missing_measurement_filter():
    query = """
    from(bucket: "sensor_data")
      |> range(start: -30d)
    """
    assert is_safe_flux_query(query) is False


def test_blocks_delete_keyword():
    query = VALID_QUERY + '\n delete()'
    assert is_safe_flux_query(query) is False


def test_blocks_drop_keyword():
    query = VALID_QUERY + '\n drop()'
    assert is_safe_flux_query(query) is False


def test_blocks_import_keyword():
    query = VALID_QUERY + '\n import "http"'
    assert is_safe_flux_query(query) is False


def test_blocks_http_keyword():
    query = VALID_QUERY + '\n http.post()'
    assert is_safe_flux_query(query) is False


def test_allows_http_substring_in_tag_name():
    """A Flux query referencing a tag with 'http' in its name should not be
    blocked. The block list targets http:// urls and http.* function calls only.
    """
    query = """
    from(bucket: "sensor_data")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
      |> filter(fn: (r) => r["http_status"] == "ok")
      |> filter(fn: (r) => r["_field"] == "temperature")
      |> mean()
    """
    assert is_safe_flux_query(query) is True


def test_blocks_experimental_keyword():
    query = VALID_QUERY + '\n experimental.to()'
    assert is_safe_flux_query(query) is False


def test_blocks_to_write_operation():
    query = VALID_QUERY + '\n |> to(bucket: "other")'
    assert is_safe_flux_query(query) is False


def test_blocks_query_without_range():
    query = """
    from(bucket: "sensor_data")
      |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
      |> filter(fn: (r) => r["_field"] == "temperature")
    """
    assert is_safe_flux_query(query) is False


def test_blocks_unknown_field_only():
    query = """
    from(bucket: "sensor_data")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
      |> filter(fn: (r) => r["_field"] == "battery_level")
    """
    assert is_safe_flux_query(query) is False


def test_passes_valid_safe_query():
    assert is_safe_flux_query(VALID_QUERY) is True


def test_run_flux_query_caps_results_at_20_records():
    mock_records = []

    for i in range(25):
        mock_record = MagicMock()

        mock_record.get_value.return_value = 20.5
        mock_record.get_time.return_value = "2026-05-10T00:00:00Z"

        mock_record.values = {
            "_field": "temperature"
        }

        mock_records.append(mock_record)

    mock_table = MagicMock()
    mock_table.records = mock_records

    mock_query_api = MagicMock()
    mock_query_api.query.return_value = [mock_table]

    mock_client = MagicMock()
    mock_client.query_api.return_value = mock_query_api

    with patch(
        "app.services.text_to_flux_service.get_influx_client",
        return_value=mock_client,
    ):
        results = run_flux_query(VALID_QUERY)

    assert len(results) == 20


def test_answer_sensor_flux_question_returns_blocked_status():
    with patch(
        "app.services.text_to_flux_service.generate_flux_from_question",
        return_value='from(bucket: "bad_bucket")',
    ):
        result = answer_sensor_flux_question(
            "Show me temperature readings"
        )

    assert result["status"] == "text_to_flux_blocked"


import app.services.text_to_flux_service as t2f


def test_is_safe_flux_query_returns_false_when_bucket_env_missing(monkeypatch):
    monkeypatch.setattr(t2f, "INFLUX_BUCKET", None)

    assert t2f.is_safe_flux_query(VALID_QUERY) is False


def test_is_safe_flux_query_returns_false_when_bucket_env_empty(monkeypatch):
    monkeypatch.setattr(t2f, "INFLUX_BUCKET", "")

    assert t2f.is_safe_flux_query(VALID_QUERY) is False