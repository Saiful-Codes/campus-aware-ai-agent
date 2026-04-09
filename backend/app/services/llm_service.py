from google import genai
from app.core.config import settings
import time

MODEL_NAME = "gemini-2.5-flash"

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_response(query: str) -> tuple[str, str]:
    prompt = f"""
You are a campus-aware university assistant.
Answer clearly, briefly, and factually.
If unsure, say so honestly.

User question: {query}
"""

    max_retries = 2
    attempt = 0
    llm_workflow_start = time.time()

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
                return response.text, "success"

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