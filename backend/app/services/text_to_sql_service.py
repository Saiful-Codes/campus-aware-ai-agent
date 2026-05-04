import os
import re
import time
from dotenv import load_dotenv
from google import genai

from app.services.sql_guard_service import is_safe_select_query
from app.services.sql_db_service import run_select_query

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


DATABASE_SCHEMA = """
You are working with a PostgreSQL database.

Table name:
sensor_readings

Columns:
- id: integer, primary key
- timestamp: timestamp with time zone, sensor reading time
- entry_id: integer, unique sensor entry ID
- temperature: double precision, temperature in Celsius
- humidity: double precision, humidity percentage
- pressure: double precision, pressure in hPa
- dew_point: double precision, dew point value
- source: text, source of the reading

Important rules:
- Only generate SELECT queries.
- Only query the sensor_readings table.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or TRUNCATE.
- Use PostgreSQL syntax.
- For latest/current readings, use ORDER BY timestamp DESC LIMIT 1.
- For historical questions, use timestamp filters.
- Return only the SQL query. Do not include explanation or markdown.
- When calculating AVG, MIN, MAX, or other numeric aggregates, exclude NaN values using column::text != 'NaN'.
"""


def clean_sql_output(text: str) -> str:
    """
    Removes markdown/code block formatting if Gemini returns it.
    """

    text = text.strip()

    text = text.replace("```sql", "")
    text = text.replace("```", "")

    return text.strip()


def generate_sql_from_question(user_question: str) -> str:
    import time

    prompt = f"""
{DATABASE_SCHEMA}

User question:
{user_question}

Generate the best SQL query:
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            sql_query = clean_sql_output(response.text)
            return sql_query

        except Exception as e:
            print(f"Gemini SQL generation attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    raise Exception("Failed to generate SQL after retries")


def format_sql_result(user_question: str, sql_query: str, query_result: list) -> str:
    prompt = f"""
You are a helpful campus sensor data assistant.

User question:
{user_question}

SQL query used:
{sql_query}

Database result:
{query_result}

Write a short, clear, human-friendly answer.
Do not mention SQL unless necessary.
If the result is empty, say that no matching sensor data was found.
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text.strip()

        except Exception as e:
            print(f"Gemini formatting attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    return f"The database query ran successfully, but I could not format the answer right now. Result: {query_result}"


def answer_sensor_database_question(user_question: str):
    """
    Full Text-to-SQL pipeline:
    question -> SQL -> safety check -> DB query -> readable answer
    """

    sql_query = generate_sql_from_question(user_question)

    print(f"Generated SQL: {sql_query}")

    if not is_safe_select_query(sql_query):
        return {
            "answer": "Sorry, I could not safely convert that question into a database query.",
            "status": "text_to_sql_blocked",
            "sql": sql_query,
            "data": [],
        }

    query_result = run_select_query(sql_query)

    answer = format_sql_result(user_question, sql_query, query_result)

    return {
        "answer": answer,
        "status": "text_to_sql_response",
        "sql": sql_query,
        "data": query_result,
    }