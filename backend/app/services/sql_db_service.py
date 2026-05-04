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


def run_select_query(sql_query: str):
    """
    Runs a safe SELECT query and returns rows as dictionaries.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(sql_query)

            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            return results

    finally:
        conn.close()