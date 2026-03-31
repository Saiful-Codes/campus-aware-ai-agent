from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_response(query: str) -> tuple[str, str]:
    try:
        prompt = f"""
You are a campus-aware intelligent assistant prototype for a university environment.

Your job is to answer clearly, briefly, and factually.
If the user asks something campus-related, try to answer helpfully.
If you are unsure or the information is not available, say that clearly instead of making up facts.
Do not pretend to have access to real-time campus databases unless that information is explicitly provided.

User question: {query}
"""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        if response.text:
            return response.text, "success"

        return "Sorry, I could not generate a response.", "error"

    except Exception:
        return "Sorry, something went wrong while generating the response.", "error"