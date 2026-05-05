import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

load_dotenv()

INFLUX_URL = os.getenv("INFLUXDB_URL")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")


def get_influx_client():
    return InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
    )


def get_latest_sensor_reading_from_influx():
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
      |> filter(fn: (r) => r["_field"] == "temperature" or r["_field"] == "humidity" or r["_field"] == "pressure" or r["_field"] == "dew_point")
      |> last()
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''

    client = get_influx_client()
    query_api = client.query_api()

    try:
        tables = query_api.query(query=query, org=INFLUX_ORG)

        for table in tables:
            for record in table.records:
                values = record.values

                return {
                    "timestamp": values.get("_time"),
                    "temperature": values.get("temperature"),
                    "humidity": values.get("humidity"),
                    "pressure": values.get("pressure"),
                    "dew_point": values.get("dew_point"),
                    "source": values.get("source", "influxdb"),
                }

        return None

    finally:
        client.close()