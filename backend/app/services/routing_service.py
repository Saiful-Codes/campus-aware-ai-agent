SENSOR_KEYWORDS = [
    "temperature",
    "humidity",
    "pressure",
    "dew point",
    "sensor",
    "stuffy",
    "hot",
    "cold",
    "air",
    "weather",
    "reading",
]


def is_sensor_query(message: str) -> bool:
    if not message:
        return False

    message_lower = message.lower()
    return any(keyword in message_lower for keyword in SENSOR_KEYWORDS)