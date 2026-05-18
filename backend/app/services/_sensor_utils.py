def safe_float(value):
    """Coerce a ThingSpeak feed field value to float, returning None on failure.

    Handles the common cases of None, empty string, and non-numeric strings.
    Lifted unchanged from sensor_service.py and influx_sensor_service.py during
    Sprint 5 Batch C dedup.
    """
    if value is None or value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None
