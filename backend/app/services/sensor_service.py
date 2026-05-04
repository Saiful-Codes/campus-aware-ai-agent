from app.services.sensor_db_service import insert_sensor_reading
import requests


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
        "temperature": float(latest_feed.get("field1")) if latest_feed.get("field1") else None,
        "humidity": float(latest_feed.get("field2")) if latest_feed.get("field2") else None,
        "pressure": float(latest_feed.get("field3")) if latest_feed.get("field3") else None,
        "dew_point": float(latest_feed.get("field4")) if latest_feed.get("field4") else None,
    }


def get_latest_sensor_data():
    try:
        raw_data = fetch_raw_sensor_data()
        cleaned_data = parse_sensor_payload(raw_data)
        return cleaned_data
    except Exception as e:
        print("Error fetching sensor data:", e)
        return None

def sync_latest_sensor_data():
    """
    Fetch latest sensor data from API and store it in DB (no duplicates).
    """

    raw_data = fetch_raw_sensor_data()
    feeds = raw_data.get("feeds", [])

    if not feeds:
        return {
            "success": False,
            "message": "No sensor data available"
        }

    latest_feed = feeds[-1]

    sensor_data = {
        "timestamp": latest_feed.get("created_at"),
        "temperature": float(latest_feed.get("field1")) if latest_feed.get("field1") else None,
        "humidity": float(latest_feed.get("field2")) if latest_feed.get("field2") else None,
        "pressure": float(latest_feed.get("field3")) if latest_feed.get("field3") else None,
        "dew_point": float(latest_feed.get("field4")) if latest_feed.get("field4") else None,
        "entry_id": latest_feed.get("entry_id"),
    }

    result = insert_sensor_reading(sensor_data)

    return {
        "success": True,
        "inserted": result["inserted"],
        "entry_id": result["entry_id"],
        "data": sensor_data
    }

def build_sensor_response(user_message: str, sensor_data: dict) -> str:
    if not sensor_data:
        return "Sorry, I could not fetch the latest sensor data right now."

    message_lower = user_message.lower()

    temperature = sensor_data.get("temperature")
    humidity = sensor_data.get("humidity")
    pressure = sensor_data.get("pressure")
    dew_point = sensor_data.get("dew_point")
    timestamp = sensor_data.get("timestamp")

    if "temperature" in message_lower or "hot" in message_lower or "cold" in message_lower:
        return f"The current temperature is {temperature}°C."

    if "humidity" in message_lower:
        return f"The current humidity is {humidity}%."

    if "pressure" in message_lower:
        return f"The current pressure is {pressure} hPa."

    if "dew point" in message_lower:
        return f"The current dew point is {dew_point}."

    if "stuffy" in message_lower or "air" in message_lower:
        return (
            f"The current temperature is {temperature}°C and humidity is {humidity}%. "
            f"It may feel a bit stuffy depending on the room conditions, "
            f"but this sensor feed does not include CO2 or airflow data, so I cannot confirm air quality precisely."
        )

    return (
        f"Latest sensor reading at {timestamp}: "
        f"temperature {temperature}°C, humidity {humidity}%, "
        f"pressure {pressure} hPa, dew point {dew_point}."
    )