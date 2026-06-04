from influxdb_client import InfluxDBClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

INFLUX_URL = os.getenv("INFLUXDB_URL")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")


def main():
    print("Connecting to InfluxDB...")

    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG
    )

    delete_api = client.delete_api()

    print("Deleting existing sensor_readings data...")

    delete_api.delete(
        start="1970-01-01T00:00:00Z",
        stop=datetime.utcnow(),
        predicate='_measurement="sensor_readings"',
        bucket=INFLUX_BUCKET,
        org=INFLUX_ORG
    )

    print("Cleanup complete!")


if __name__ == "__main__":
    main()