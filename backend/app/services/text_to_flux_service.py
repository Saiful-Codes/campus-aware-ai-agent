import os
import re
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
  from(bucket: "{INFLUX_BUCKET}")
    |> range(start: -30d)
    |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
    |> filter(fn: (r) => r["_field"] == "temperature")
    |> group()
    |> max()
- For average temperature, use group() |> mean().
- For count queries, use group() |> count().
- For temperature trends over time, generate:
  from(bucket: "{INFLUX_BUCKET}")
    |> range(start: -7d)
    |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
    |> filter(fn: (r) => r["_field"] == "temperature")
    |> aggregateWindow(every: 1h, fn: mean)
    |> limit(n: 20)
- Never query the entire bucket without a range().
- Never use range(start: 0).
- Always keep query results small and efficient.
- Prefer aggregate queries over raw row outputs.
- If the user asks for trends over time, use aggregateWindow().
- For trend queries, use aggregateWindow(every: 1h, fn: mean).
- Never return more than 20 rows.
- Avoid returning raw ungrouped sensor records unless explicitly requested.
- If the question is ambiguous, prefer safe aggregate summaries.
- Always include limit(n: 20) for non-aggregate queries.
"""

def clean_flux_output(text: str) -> str:
    text = text.strip()
    text = text.replace("```flux", "")
    text = text.replace("```", "")

    cleaned = text.strip()
    cleaned_lower = cleaned.lower()

    # Add safety limit automatically for raw queries
    has_limit = "limit(" in cleaned_lower

    has_aggregate = any(
        agg in cleaned_lower
        for agg in [
            "mean()",
            "max()",
            "min()",
            "count()",
            "aggregatewindow",
        ]
    )

    if not has_limit and not has_aggregate:
        cleaned += '\n  |> limit(n: 20)'

    return cleaned


SENSOR_FIELDS = frozenset({"temperature", "humidity", "pressure", "dew_point"})

_YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')

# Matches phrases like "last 7 days", "past 14 days", "last 3 weeks", "last 6 hours".
# Requires a digit, so explicit phrases like "last week" / "this month" are unaffected.
_RELATIVE_N_UNITS_PATTERN = re.compile(
    r'\b(last|past)\s+(\d+)\s+(hour|day|week|month|year)s?\b'
)

_UNIT_TO_DAYS = {"day": 1, "week": 7, "month": 30, "year": 365}

_MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def get_time_range_info(user_question: str) -> dict:
    """Translate a natural-language time phrase into a Flux range expression + human label.

    Returns a dict with:
        flux_range  — e.g. "start: -7d" or "start: 2026-04-01T00:00:00Z, stop: 2026-05-01T00:00:00Z"
        label       — human-readable description, e.g. "this week" or "April 2026"
    """
    q = user_question.lower()

    # Month + year wins over year-only (check first)
    for month_name, month_num in _MONTH_MAP.items():
        if month_name in q:
            year_match = _YEAR_PATTERN.search(q)
            if year_match:
                year = int(year_match.group())
                next_month = month_num + 1 if month_num < 12 else 1
                next_year = year if month_num < 12 else year + 1
                start = f"{year:04d}-{month_num:02d}-01T00:00:00Z"
                stop = f"{next_year:04d}-{next_month:02d}-01T00:00:00Z"
                label = f"{month_name.capitalize()} {year}"
                return {"flux_range": f"start: {start}, stop: {stop}", "label": label}

    # Year-only (e.g. "in 1995", "readings from 2024")
    year_match = _YEAR_PATTERN.search(q)
    if year_match:
        year = int(year_match.group())
        start = f"{year:04d}-01-01T00:00:00Z"
        stop = f"{year + 1:04d}-01-01T00:00:00Z"
        return {"flux_range": f"start: {start}, stop: {stop}", "label": str(year)}

    # Numeric relative phrases ("last 7 days", "past 3 weeks", "last 6 hours").
    # Requires a digit, so the explicit branches below ("last week", "this month")
    # still take their own paths.
    n_match = _RELATIVE_N_UNITS_PATTERN.search(q)
    if n_match:
        prep, n_str, unit = n_match.group(1), n_match.group(2), n_match.group(3)
        n = int(n_str)
        if unit == "hour":
            flux_range = f"start: -{n}h"
        else:
            days = n * _UNIT_TO_DAYS[unit]
            flux_range = f"start: -{days}d"
        plural = unit if n == 1 else f"{unit}s"
        return {"flux_range": flux_range, "label": f"the {prep} {n} {plural}"}

    # Relative keywords — ordered most-specific first
    if "last hour" in q or "past hour" in q:
        return {"flux_range": "start: -1h", "label": "the last hour"}
    if "today" in q:
        return {"flux_range": "start: -24h", "label": "today"}
    if "yesterday" in q:
        return {"flux_range": "start: -48h", "label": "yesterday"}
    if "this week" in q or "current week" in q:
        return {"flux_range": "start: -7d", "label": "this week"}
    if "last week" in q or "past week" in q:
        return {"flux_range": "start: -14d", "label": "last week"}
    if "this month" in q or "current month" in q:
        return {"flux_range": "start: -30d", "label": "this month"}
    if "last month" in q or "past month" in q:
        return {"flux_range": "start: -60d", "label": "last month"}
    if "last year" in q or "this year" in q or "past year" in q:
        return {"flux_range": "start: -365d", "label": "this year"}

    return {"flux_range": "start: -30d", "label": "the last 30 days"}


_FIELD_HUMAN_LABEL = {
    "temperature": "temperature",
    "humidity": "humidity",
    "pressure": "pressure",
    "dew_point": "dew point",
}

_FIELD_KEYWORD_TO_FIELD = {
    "temperature": "temperature",
    "humidity": "humidity",
    "pressure": "pressure",
    "dew point": "dew_point",
}


def _detect_sensor_field(question: str) -> str | None:
    """Return the snake_case sensor field name if exactly one is mentioned.

    Returns None for zero matches or multiple matches.
    """
    q = (question or "").lower()
    matched = {field for keyword, field in _FIELD_KEYWORD_TO_FIELD.items() if keyword in q}
    if len(matched) == 1:
        return next(iter(matched))
    return None


def _build_no_data_message(time_label: str, field_label: str | None = None) -> str:
    if field_label is None:
        return (
            f"No matching sensor data was found for {time_label}. "
            "The database may not contain readings for that time range."
        )
    human = _FIELD_HUMAN_LABEL.get(field_label, field_label)
    return (
        f"No {human} readings were found for {time_label}. "
        f"The database may not contain {human} data for that period."
    )


def _parse_record_values(values: dict, raw_value, raw_time, fallback_field: str | None = None) -> dict | None:
    """Parse a FluxRecord's raw fields into a clean result dict.

    Returns None for records that should be skipped:
    - null/None values (empty aggregateWindow windows)
    - metadata or unknown field names (_time, _measurement, etc.)
    - pivot() records where no known sensor column is present
    - aggregate records (group() |> mean()) with no fallback_field hint

    Args:
        values:         record.values dict from FluxRecord
        raw_value:      result of record.get_value() (the _value column)
        raw_time:       result of record.get_time() (datetime or None)
        fallback_field: sensor field name detected from the user question.
                        Used only when both _field and any sensor-named column
                        are absent (group() + aggregate drops _field).
    """
    field = values.get("_field")
    value = raw_value

    # For pivot() results, _field is absent; sensor field names become column keys
    if field is None or field not in SENSOR_FIELDS:
        for known in SENSOR_FIELDS:
            if known in values:
                field = known
                v = values[known]
                value = round(v, 2) if isinstance(v, float) else v
                break

    # Aggregate result: group() |> mean() drops _field entirely, leaving only
    # _value. Fall back to the field detected from the user question, but only
    # if it's a known sensor field.
    if (field is None or field not in SENSOR_FIELDS) and fallback_field in SENSOR_FIELDS:
        field = fallback_field

    if field is None or field not in SENSOR_FIELDS:
        return None

    if value is None:
        return None

    if isinstance(value, float):
        value = round(value, 2)

    try:
        time_str = str(raw_time) if raw_time is not None else None
    except Exception:
        time_str = None

    return {"time": time_str, "field": field, "value": value}


def generate_flux_from_question(user_question: str) -> str:
    time_info = get_time_range_info(user_question)
    flux_range = time_info["flux_range"]
    prompt = f"""
{FLUX_SCHEMA}

Default time range (use inside range()):
{flux_range}

Important:
- Use |> range({flux_range}) unless the user clearly specifies a different period.
- For absolute ranges like "start: 2026-04-01T00:00:00Z, stop: 2026-05-01T00:00:00Z", use them exactly as given.

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

    # Defensive guard: if INFLUXDB_BUCKET env is missing/empty, refuse to
    # validate. Returning False routes the request through the existing
    # text_to_flux_blocked status instead of raising 500.
    if not INFLUX_BUCKET:
        print("is_safe_flux_query blocked: INFLUXDB_BUCKET env var is not set")
        return False

    blocked_terms = [
        "delete",
        "drop",
        "import ",
        "http://",
        "https://",
        "http.",
        "experimental",
        "to(",
    ]

    # Must use correct bucket
    if f'from(bucket: "{INFLUX_BUCKET.lower()}"' not in query:
        return False

    # Must include measurement filter
    if ('r["_measurement"] == "sensor_readings"' not in query and 'r._measurement == "sensor_readings"' not in query):
        return False

    # Must include range()
    if "range(" not in query:
        return False
    
    # Must reference at least one approved sensor field
    if not any(field in query for field in SENSOR_FIELDS):
        return False

    # Block dangerous terms
    for term in blocked_terms:
        if term in query:
            return False

    return True


def run_flux_query(flux_query: str, fallback_field: str | None = None):
    influx_client = get_influx_client()
    query_api = influx_client.query_api()

    try:
        try:
            tables = query_api.query(query=flux_query, org=INFLUX_ORG)
        except Exception as e:
            print(f"Influx query execution failed: {e}")
            return []

        results = []

        for table in tables:
            for record in table.records:
                try:
                    raw_value = record.get_value()
                except Exception:
                    continue

                # Aggregate records (group() |> mean()) drop the _time column;
                # treat that as no-time rather than skipping the whole record.
                try:
                    raw_time = record.get_time()
                except Exception:
                    raw_time = None

                parsed = _parse_record_values(
                    record.values, raw_value, raw_time, fallback_field=fallback_field
                )
                if parsed is not None:
                    results.append(parsed)

        return results[:20]

    finally:
        influx_client.close()


_FIELD_UNITS = {
    "temperature": "°C",
    "humidity": "%",
    "pressure": "hPa",
    "dew_point": "°C",
}


def _format_records_for_prompt(records: list) -> str:
    """Render Flux result records as one human-readable line per record.

    Example output:
        temperature: 22.3 °C at 2026-05-15T10:00:00Z
        humidity: 58.0 % at 2026-05-15T10:00:00Z
    """
    if not records:
        return ""

    lines = []

    for record in records:
        field = record.get("field", "value")
        value = record.get("value")
        time_str = record.get("time")
        unit = _FIELD_UNITS.get(field, "")

        value_part = f"{field}: {value} {unit}".rstrip()

        if time_str:
            lines.append(f"{value_part} at {time_str}")
        else:
            lines.append(value_part)

    return "\n".join(lines)


def format_flux_result(
    user_question: str,
    flux_query: str,
    query_result: list,
    time_label: str = "the requested time range",
) -> str:
    record_count = len(query_result)
    is_time_series = record_count > 1

    prompt = f"""
You are a helpful campus sensor data assistant.

User question:
{user_question}

The user asked about: {time_label}.
If you mention the time period in your answer, use phrasing consistent with "{time_label}".

Sensor data result ({record_count} record{"s" if record_count != 1 else ""}):
{_format_records_for_prompt(query_result)}

Rules:
- Answer in under 100 words.
- Do not mention Flux, JSON, InfluxDB, or raw data structures.
- Do not invent explanations for missing data or gaps — only describe what is actually in the result.
- Do not say "no data was recorded" unless the result is genuinely empty.
{"- Multiple records: describe the overall trend, range, or pattern across all of them." if is_time_series else "- Single record: report the value directly and clearly."}
- Round sensor values sensibly in your answer.
- Be natural and conversational.
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
    time_info = get_time_range_info(user_question)
    flux_query = generate_flux_from_question(user_question)

    print("\n===== GENERATED FLUX QUERY =====")
    print(flux_query)
    print("================================\n")

    if not is_safe_flux_query(flux_query):
        return {
            "answer": "Sorry, I could not safely convert that question into an InfluxDB query.",
            "status": "text_to_flux_blocked",
            "flux": flux_query,
            "data": [],
        }

    field_label = _detect_sensor_field(user_question)
    query_result = run_flux_query(flux_query, fallback_field=field_label)

    if not query_result:
        return {
            "answer": _build_no_data_message(time_info["label"], field_label=field_label),
            "status": "text_to_flux_no_data",
            "flux": flux_query,
            "data": [],
        }

    try:
        answer = format_flux_result(
            user_question,
            flux_query,
            query_result,
            time_label=time_info["label"],
        )

    except Exception as e:
        print(f"Flux formatting fallback triggered: {e}")

        answer = (
            "The sensor query completed successfully, "
            "but the response formatter failed."
        )

    return {
        "answer": answer,
        "status": "text_to_flux_response",
        "flux": flux_query,
        "data": query_result,
    }