from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(
    prompt: str,
    response_schema=None,
):
    config = None

    if response_schema:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    if response_schema:
        return response.parsed

    return response.text