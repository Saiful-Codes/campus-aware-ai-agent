import requests

from app.services._sensor_utils import safe_float


URL = "https://api.thingspeak.com/channels/270748/feeds.json?results=2"


def fetch_raw_sensor_data():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_sensor_payload(raw_data):
    feeds = raw_data.get("feeds", [])

    if not feeds:
        return None

    latest_feed = feeds[-1]

    return {
        "timestamp": latest_feed.get("created_at"),
        "entry_id": latest_feed.get("entry_id"),
        "temperature": safe_float(latest_feed.get("field1")),
        "humidity": safe_float(latest_feed.get("field2")),
        "pressure": safe_float(latest_feed.get("field3")),
        "dew_point": safe_float(latest_feed.get("field4")),
    }


def get_latest_sensor_data():
    try:
        raw_data = fetch_raw_sensor_data()
        return parse_sensor_payload(raw_data)

    except Exception as e:
        print("Error fetching sensor data:", e)
        return None


def sync_latest_sensor_data():
    """
    Legacy-compatible function.

    This now only fetches the latest live sensor data from the API.
    It does NOT write to PostgreSQL anymore.
    InfluxDB writing is handled by influx_sensor_service.py.
    """

    sensor_data = get_latest_sensor_data()

    if not sensor_data:
        return {
            "success": False,
            "message": "No sensor data available",
        }

    return {
        "success": True,
        "data": sensor_data,
    }
