import os
import math
import psycopg2
from dotenv import load_dotenv

load_dotenv()

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


def clean_value(value):
    if value is None:
        return None

    try:
        number = float(value)
        if math.isnan(number):
            return None
        return number
    except (ValueError, TypeError):
        return None


def insert_sensor_reading(reading: dict):
    """
    Insert one sensor reading into PostgreSQL.
    Duplicate entry_id values are ignored safely.
    """

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
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (entry_id) DO NOTHING
    RETURNING id;
    """

    values = (
        reading.get("timestamp"),
        reading.get("entry_id"),
        clean_value(reading.get("temperature")),
        clean_value(reading.get("humidity")),
        clean_value(reading.get("pressure")),
        clean_value(reading.get("dew_point")),
        reading.get("source", "live_sensor_api"),
    )

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(insert_sql, values)
            inserted_row = cur.fetchone()
            conn.commit()

            return {
                "inserted": inserted_row is not None,
                "database_id": inserted_row[0] if inserted_row else None,
                "entry_id": reading.get("entry_id"),
            }
    finally:
        conn.close()


def get_latest_sensor_reading_from_db():
    query = """
    SELECT 
        timestamp,
        entry_id,
        temperature,
        humidity,
        pressure,
        dew_point,
        source
    FROM sensor_readings
    ORDER BY timestamp DESC
    LIMIT 1;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()

            if not row:
                return None

            return {
                "timestamp": row[0],
                "entry_id": row[1],
                "temperature": row[2],
                "humidity": row[3],
                "pressure": row[4],
                "dew_point": row[5],
                "source": row[6],
            }
    finally:
        conn.close()