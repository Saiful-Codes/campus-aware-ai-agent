import os
import time
from dotenv import load_dotenv
from google import genai

from app.services.influx_query_service import get_influx_client

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

INFLUX_ORG = os.getenv("INFLUXDB_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")


FLUX_SCHEMA = f"""
You are working with InfluxDB using Flux query language.

Bucket:
{INFLUX_BUCKET}

Measurement:
sensor_readings

Fields:
- temperature: temperature in Celsius
- humidity: humidity percentage
- pressure: pressure in hPa
- dew_point: dew point value

Tags:
- source
- entry_id

Important Flux rules:
- Always query from bucket "{INFLUX_BUCKET}".
- Always filter _measurement == "sensor_readings".
- Only use these fields: temperature, humidity, pressure, dew_point.
- Return only Flux query code.
- Do not use markdown.
- Do not explain the query.
- For latest/current reading, use range(start: -30d) and last().
- For averages, use mean().
- For highest values, use max().
- For lowest values, use min().
- For counts, use count().
- Use pivot only when returning multiple fields together.
- For max(), min(), mean(), and count(), use group() before the aggregate so the result is a single overall value.
- For highest temperature, generate:
  from(bucket: "sensor_data")
    |> range(start: -30d)
    |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
    |> filter(fn: (r) => r["_field"] == "temperature")
    |> group()
    |> max()
- For average temperature, use group() |> mean().
- For count queries, use group() |> count().
"""


def clean_flux_output(text: str) -> str:
    text = text.strip()
    text = text.replace("```flux", "")
    text = text.replace("```", "")
    return text.strip()


def generate_flux_from_question(user_question: str) -> str:
    prompt = f"""
{FLUX_SCHEMA}

User question:
{user_question}

Generate the best Flux query:
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return clean_flux_output(response.text)

        except Exception as e:
            print(f"Gemini Flux generation attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    raise Exception("Failed to generate Flux query after retries")


def is_safe_flux_query(flux_query: str) -> bool:
    if not flux_query:
        return False

    query = flux_query.lower()

    blocked_terms = [
        "delete",
        "drop",
        "import ",
        "http",
        "experimental",
        "to(",
        "from(bucket:",
    ]

    if f'from(bucket: "{INFLUX_BUCKET.lower()}"' not in query:
        return False

    if 'r["_measurement"] == "sensor_readings"' not in query and 'r._measurement == "sensor_readings"' not in query:
        return False

    for term in blocked_terms:
        if term == "from(bucket:":
            continue
        if term in query:
            return False

    return True


def run_flux_query(flux_query: str):
    client = get_influx_client()
    query_api = client.query_api()

    try:
        tables = query_api.query(query=flux_query, org=INFLUX_ORG)

        results = []

        for table in tables:
            for record in table.records:
                results.append(record.values)

        return results

    finally:
        client.close()


def format_flux_result(user_question: str, flux_query: str, query_result: list) -> str:
    prompt = f"""
You are a helpful campus sensor data assistant.

User question:
{user_question}

Flux query used:
{flux_query}

InfluxDB result:
{query_result}

Write a short, clear, human-friendly answer.
Do not mention Flux unless necessary.
If no data is found, say no matching sensor data was found.
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text.strip()

        except Exception as e:
            print(f"Gemini Flux formatting attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    return f"The InfluxDB query ran successfully, but I could not format the answer. Result: {query_result}"


def answer_sensor_flux_question(user_question: str):
    flux_query = generate_flux_from_question(user_question)

    print(f"Generated Flux:\n{flux_query}")

    if not is_safe_flux_query(flux_query):
        return {
            "answer": "Sorry, I could not safely convert that question into an InfluxDB query.",
            "status": "text_to_flux_blocked",
            "flux": flux_query,
            "data": [],
        }

    query_result = run_flux_query(flux_query)

    answer = format_flux_result(user_question, flux_query, query_result)

    return {
        "answer": answer,
        "status": "text_to_flux_response",
        "flux": flux_query,
        "data": query_result,
    }