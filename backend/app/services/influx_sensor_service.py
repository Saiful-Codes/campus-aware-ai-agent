import os
import requests
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

INFLUX_URL = os.getenv("INFLUXDB_URL")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")

URL = "https://api.thingspeak.com/channels/270748/feeds.json?results=2"


def fetch_latest_feed():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()

    data = response.json()
    feeds = data.get("feeds", [])

    if not feeds:
        return None

    return feeds[-1]


def safe_float(value):
    if value is None or value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def write_feed_to_influx(feed: dict):
    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = (
        Point("sensor_readings")
        .tag("source", "live_sensor_api")
        .tag("entry_id", str(feed.get("entry_id")))
        .time(feed.get("created_at"), WritePrecision.NS)
    )

    fields = {
        "temperature": safe_float(feed.get("field1")),
        "humidity": safe_float(feed.get("field2")),
        "pressure": safe_float(feed.get("field3")),
        "dew_point": safe_float(feed.get("field4")),
    }

    for field_name, field_value in fields.items():
        if field_value is not None:
            point.field(field_name, field_value)

    write_api.write(
        bucket=INFLUX_BUCKET,
        org=INFLUX_ORG,
        record=point,
    )

    client.close()

    return {
        "timestamp": feed.get("created_at"),
        "entry_id": feed.get("entry_id"),
        **fields,
    }


def sync_latest_sensor_data_to_influx():
    try:
        feed = fetch_latest_feed()

        if not feed:
            return {
                "success": False,
                "message": "No latest sensor feed found",
            }

        data = write_feed_to_influx(feed)

        return {
            "success": True,
            "inserted": True,
            "entry_id": feed.get("entry_id"),
            "data": data,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }