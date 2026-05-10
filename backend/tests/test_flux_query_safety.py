from app.services.text_to_flux_service import is_safe_flux_query


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