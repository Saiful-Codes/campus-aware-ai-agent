import os
import time
from typing import Tuple

from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=API_KEY)


def generate_response(query: str) -> Tuple[str, str]:
    llm_workflow_start = time.time()
    max_retries = 2
    attempt = 0

    prompt = f"""
You are Campus AI, a helpful campus assistant.

Answer the user's question clearly and naturally.
Keep the answer concise but useful.
If the question is about campus directions, campus information, or general help, respond in a practical and friendly way.

User question:
{query}
"""

    while attempt <= max_retries:
        attempt_start = time.time()

        try:
            print(f"Using model: {MODEL_NAME}")
            print(f"Starting Gemini call... Attempt {attempt + 1}")

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            attempt_end = time.time()
            attempt_time = attempt_end - attempt_start
            print(f"Attempt {attempt + 1} succeeded in {attempt_time:.2f} seconds")

            total_llm_time = time.time() - llm_workflow_start
            print(f"Total LLM workflow time: {total_llm_time:.2f} seconds")

            if response.text:
                return response.text.strip(), "success"

            return "Sorry, I could not generate a response.", "error"

        except Exception as e:
            attempt_end = time.time()
            attempt_time = attempt_end - attempt_start
            print(f"Attempt {attempt + 1} failed after {attempt_time:.2f} seconds")
            print(f"Error in generate_response: {e}")

            error_text = str(e)

            if "503" in error_text and attempt < max_retries:
                wait_time = 2 * (attempt + 1)
                print(f"503 error detected. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
                continue

            total_llm_time = time.time() - llm_workflow_start
            print(f"Total LLM workflow time: {total_llm_time:.2f} seconds")
            return "Sorry, the AI service is busy right now. Please try again in a moment.", "error"


def generate_sensor_response(query: str, sensor_data: dict) -> Tuple[str, str]:
    llm_workflow_start = time.time()
    max_retries = 2
    attempt = 0

    temperature = sensor_data.get("temperature", "unknown")
    humidity = sensor_data.get("humidity", "unknown")
    pressure = sensor_data.get("pressure", "unknown")
    dew_point = sensor_data.get("dew_point", "unknown")
    timestamp = sensor_data.get("timestamp", "unknown")

    prompt = f"""
You are Campus AI, a helpful campus assistant with access to live IoT sensor data.

The user asked a sensor-related question. Use ONLY the live sensor data below to answer.
Do not make up values.
Do not mention raw JSON or backend logic.
Answer naturally, clearly, and briefly.
If useful, include a short interpretation such as whether the condition seems comfortable or normal.
Keep the response to 1-3 sentences.

Live sensor data:
- Temperature: {temperature} °C
- Humidity: {humidity} %
- Pressure: {pressure} hPa
- Dew Point: {dew_point} °C
- Timestamp: {timestamp}

User question:
{query}
"""

    while attempt <= max_retries:
        attempt_start = time.time()

        try:
            print(f"Using model for sensor response: {MODEL_NAME}")
            print(f"Starting Gemini sensor call... Attempt {attempt + 1}")

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            attempt_end = time.time()
            attempt_time = attempt_end - attempt_start
            print(f"Sensor attempt {attempt + 1} succeeded in {attempt_time:.2f} seconds")

            total_llm_time = time.time() - llm_workflow_start
            print(f"Total sensor LLM workflow time: {total_llm_time:.2f} seconds")

            if response.text:
                return response.text.strip(), "sensor_response"

            return "Sorry, I could not generate a sensor-based response.", "error"

        except Exception as e:
            attempt_end = time.time()
            attempt_time = attempt_end - attempt_start
            print(f"Sensor attempt {attempt + 1} failed after {attempt_time:.2f} seconds")
            print(f"Error in generate_sensor_response: {e}")

            error_text = str(e)

            if "503" in error_text and attempt < max_retries:
                wait_time = 2 * (attempt + 1)
                print(f"503 error detected in sensor response. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
                continue

            total_llm_time = time.time() - llm_workflow_start
            print(f"Total sensor LLM workflow time: {total_llm_time:.2f} seconds")
            return "Sorry, the AI service is busy right now. Please try again in a moment.", "error"