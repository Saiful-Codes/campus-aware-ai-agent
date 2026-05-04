import os
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


def main():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                ALTER TABLE sensor_readings
                ADD CONSTRAINT unique_sensor_entry_id UNIQUE (entry_id);
            """)
            conn.commit()
            print("Unique constraint added on entry_id.")
    except psycopg2.errors.DuplicateObject:
        conn.rollback()
        print("Constraint already exists. No problem.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()