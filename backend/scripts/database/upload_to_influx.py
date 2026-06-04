import os
import pandas as pd
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

INFLUX_URL = os.getenv("INFLUXDB_URL")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")

CSV_PATH = "data/sensor/processed/sensor_data_clean.csv"


def add_field_if_valid(point: Point, field_name: str, value):
    if pd.notna(value):
        point.field(field_name, float(value))
    return point


def main():
    print("Connecting to InfluxDB...")

    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)

    print("Loading CSV...")
    df = pd.read_csv(CSV_PATH)

    print(f"Total rows: {len(df)}")

    points = []

    for i, row in df.iterrows():
        try:
            point = (
                Point("sensor_readings")
                .tag("source", str(row.get("source", "1_year_sensor_dataset")))
                .tag("entry_id", str(row.get("entry_id")))
                .time(pd.to_datetime(row["timestamp"]), WritePrecision.NS)
            )

            point = add_field_if_valid(point, "temperature", row["temperature"])
            point = add_field_if_valid(point, "humidity", row["humidity"])
            point = add_field_if_valid(point, "pressure", row["pressure"])
            point = add_field_if_valid(point, "dew_point", row["dew_point"])

            points.append(point)

        except Exception as e:
            print(f"Error preparing row {i}: {e}")

        if i % 10000 == 0:
            print(f"{i} rows prepared...")

    print("Writing batch to InfluxDB...")
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=points)

    client.close()

    print(f"Upload complete! Total points written: {len(points)}")


if __name__ == "__main__":
    main()