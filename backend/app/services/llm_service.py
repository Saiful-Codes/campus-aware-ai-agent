import os
import time
from typing import Tuple

from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=API_KEY)


class GeminiCallError(RuntimeError):
    """Raised when all retries are exhausted or a non-retryable error occurs."""


_RETRYABLE_STATUS_CODES = ("429", "500", "502", "503", "504")


def call_gemini_with_retry(
    prompt: str,
    label: str = "gemini",
    max_retries: int = 2,
) -> str:
    """Call Gemini with linear backoff (2s, 4s) on transient errors.

    Returns:
        Stripped response text on success.
        Empty string "" if Gemini responded with no text (e.g. safety filter).

    Raises:
        GeminiCallError if all retries exhausted or non-retryable error.
    """
    workflow_start = time.time()
    attempt = 0
    last_error: Exception | None = None

    while attempt <= max_retries:
        try:
            print(f"[{label}] Gemini attempt {attempt + 1}...")
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            elapsed = time.time() - workflow_start
            print(f"[{label}] Succeeded after {elapsed:.2f}s on attempt {attempt + 1}")
            return response.text.strip() if response.text else ""

        except Exception as e:
            last_error = e
            error_text = str(e)
            is_retryable = any(code in error_text for code in _RETRYABLE_STATUS_CODES)
            print(f"[{label}] Attempt {attempt + 1} failed: {e}")

            if is_retryable and attempt < max_retries:
                wait_time = 2 * (attempt + 1)
                print(f"[{label}] Retryable error — sleeping {wait_time}s")
                time.sleep(wait_time)
                attempt += 1
                continue

            elapsed = time.time() - workflow_start
            print(f"[{label}] Terminal failure after {elapsed:.2f}s")
            raise GeminiCallError(f"{label} call failed: {e}") from e

    raise GeminiCallError(f"{label} retries exhausted: {last_error}")


def generate_response(query: str) -> Tuple[str, str]:
    prompt = f"""
You are Campus AI, a helpful campus assistant for La Trobe University.

Answer the user's question clearly and naturally.
Keep the answer concise but useful.
If the question is about campus directions, campus information, or general help, respond in a practical and friendly way.
Do not invent specific La Trobe links, fees, or current dates.
If the question asks for exact current information (fees, calendar, links, policies), suggest checking latrobe.edu.au directly.

User question:
{query}
"""

    try:
        text = call_gemini_with_retry(prompt, label="generate_response")
    except GeminiCallError:
        return "Sorry, the AI service is busy right now. Please try again in a moment.", "error"

    if not text:
        return (
            "I couldn't generate a reliable answer for that question. "
            "Please try rephrasing or simplifying your request.",
            "error",
        )

    return text, "success"


def generate_sensor_response(query: str, sensor_data: dict) -> Tuple[str, str]:
    if not sensor_data:
        return (
            "No recent sensor data is available at the moment. Please try again shortly.",
            "sensor_no_data",
        )

    temperature = sensor_data.get("temperature", "unknown")
    humidity = sensor_data.get("humidity", "unknown")
    pressure = sensor_data.get("pressure", "unknown")
    dew_point = sensor_data.get("dew_point", "unknown")
    timestamp = sensor_data.get("timestamp", "unknown")

    prompt = f"""
You are Campus AI, a helpful campus assistant for La Trobe University.

The user asked about current campus conditions. Use ONLY the sensor readings below to answer.
Do not make up values.
Do not mention sensors, IoT, JSON, databases, or any backend system names.
Answer naturally and briefly — 1 to 3 sentences maximum.
If useful, add a short human interpretation (e.g. whether the temperature feels comfortable).

Live sensor data:
- Temperature: {temperature} °C
- Humidity: {humidity} %
- Pressure: {pressure} hPa
- Dew Point: {dew_point} °C
- Timestamp: {timestamp}

User question:
{query}
"""

    try:
        text = call_gemini_with_retry(prompt, label="generate_sensor_response")
    except GeminiCallError:
        return "Sorry, the AI service is busy right now. Please try again in a moment.", "error"

    if not text:
        return (
            "I couldn't generate a reliable answer for that question. "
            "Please try rephrasing or simplifying your request.",
            "error",
        )

    return text, "sensor_response"


def generate_hybrid_response(query: str, context_chunks: list[str]) -> Tuple[str, str]:
    context = "\n\n".join(context_chunks[:4]) if context_chunks else ""

    prompt = f"""
You are Campus AI, a helpful assistant for La Trobe University students.

{"Use the document snippets below as your primary source of information." if context else "No relevant document context was found for this question."}

{"Document snippets:" if context else ""}
{context}

Rules:
- Do not invent exact links, fees, dates, or current policy values.
- If a specific La Trobe detail is not present in the snippets above, say you are not certain and suggest checking latrobe.edu.au for accuracy.
- If no context was found, give a helpful general answer but clearly state you cannot confirm La Trobe-specific details.
- Keep the answer concise.

User question:
{query}
"""

    try:
        text = call_gemini_with_retry(prompt, label="generate_hybrid_response")
    except GeminiCallError:
        return "Sorry, the AI service is busy right now. Please try again in a moment.", "error"

    if not text:
        return (
            "I couldn't generate a reliable answer for that question. "
            "Please try rephrasing or simplifying your request.",
            "error",
        )

    return text, "hybrid_response"