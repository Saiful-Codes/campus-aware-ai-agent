import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.influx_sensor_service import _build_sensor_point


def test_build_sensor_point_includes_entry_id_when_present():
    feed = {
        "created_at": "2026-05-18T10:00:00Z",
        "entry_id": 42,
        "field1": "22.5",
        "field2": "55.0",
        "field3": "1013.2",
        "field4": "12.5",
    }
    point = _build_sensor_point(feed)
    line = point.to_line_protocol()
    assert "entry_id=42" in line


def test_build_sensor_point_omits_entry_id_tag_when_none():
    feed = {
        "created_at": "2026-05-18T10:00:00Z",
        "entry_id": None,
        "field1": "22.5",
        "field2": "55.0",
        "field3": "1013.2",
        "field4": "12.5",
    }
    point = _build_sensor_point(feed)
    line = point.to_line_protocol()
    # Tag must be absent entirely — not the literal string "None".
    assert "entry_id" not in line
    assert "None" not in line


def test_build_sensor_point_omits_entry_id_tag_when_missing():
    feed = {
        "created_at": "2026-05-18T10:00:00Z",
        # entry_id key not present at all
        "field1": "22.5",
        "field2": "55.0",
        "field3": "1013.2",
        "field4": "12.5",
    }
    point = _build_sensor_point(feed)
    line = point.to_line_protocol()
    assert "entry_id" not in line
