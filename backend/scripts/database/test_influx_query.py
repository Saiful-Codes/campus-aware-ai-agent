from app.services.influx_query_service import get_latest_sensor_reading_from_influx

result = get_latest_sensor_reading_from_influx()
print(result)