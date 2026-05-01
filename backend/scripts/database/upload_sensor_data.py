import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

CSV_PATH = "data/sensor/processed/sensor_data_clean.csv"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def create_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL,
        entry_id INTEGER,
        temperature DOUBLE PRECISION,
        humidity DOUBLE PRECISION,
        pressure DOUBLE PRECISION,
        dew_point DOUBLE PRECISION,
        source TEXT
    );
    """

    with conn.cursor() as cur:
        cur.execute(create_table_sql)
        conn.commit()


def clear_existing_data(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE sensor_readings RESTART IDENTITY;")
        conn.commit()


def upload_data(conn):
    df = pd.read_csv(CSV_PATH)

    records = df[[
        "timestamp",
        "entry_id",
        "temperature",
        "humidity",
        "pressure",
        "dew_point",
        "source",
    ]].values.tolist()

    insert_sql = """
    INSERT INTO sensor_readings (
        timestamp,
        entry_id,
        temperature,
        humidity,
        pressure,
        dew_point,
        source
    )
    VALUES %s;
    """

    with conn.cursor() as cur:
        execute_values(cur, insert_sql, records)
        conn.commit()

    print(f"Uploaded {len(records)} rows into sensor_readings.")


def verify_upload(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM sensor_readings;")
        total_rows = cur.fetchone()[0]

        cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM sensor_readings;")
        min_time, max_time = cur.fetchone()

        cur.execute("SELECT * FROM sensor_readings ORDER BY timestamp LIMIT 5;")
        sample_rows = cur.fetchall()

    print("\nVerification complete")
    print("Total rows:", total_rows)
    print("Time range:", min_time, "to", max_time)
    print("\nFirst 5 rows:")
    for row in sample_rows:
        print(row)


def main():
    conn = get_connection()

    try:
        create_table(conn)
        clear_existing_data(conn)
        upload_data(conn)
        verify_upload(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()