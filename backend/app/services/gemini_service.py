from google.genai import errors
from app.config import GEMINI_API_KEY
from google.genai import types
from google import genai
import time
import random
import logging


logger = logging.getLogger(__name__)


class GeminiServiceUnavailable(Exception):
    """Raised when Gemini remains unavailable after retries."""


client = genai.Client(api_key=GEMINI_API_KEY)

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0
MAX_RETRY_DELAY = 8.0


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

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config,
            )

            if response_schema:
                if response.parsed is None:
                    raise ValueError(
                        "Gemini returned no structured response"
                    )
                return response.parsed

            if response.text is None:
                raise ValueError(
                    "Gemini returned an empty response"
                )

            return response.text

        except Exception as exc:
            if not is_retryable_error(exc):
                logger.exception("Gemini request failed")
                raise

            if attempt == MAX_RETRIES:
                logger.exception(
                    "Gemini retries exhausted after %s attempts",
                    attempt + 1,
                )
                raise GeminiServiceUnavailable(
                    "Gemini is temporarily unavailable. "
                    "Please try again later."
                ) from exc

            delay = min(
                INITIAL_RETRY_DELAY * (2 ** attempt),
                MAX_RETRY_DELAY,
            )
            delay += random.uniform(0, 0.25)

            logger.warning(
                "Temporary Gemini failure. Retrying in %.2f seconds "
                "(attempt %s of %s)",
                delay,
                attempt + 1,
                MAX_RETRIES,
            )

            time.sleep(delay)


def is_retryable_error(exc: Exception) -> bool:
    """Return True for temporary Gemini API errors."""

    if isinstance(exc, errors.APIError):
        return exc.code in (429, 500, 502, 503, 504)

    status_code = getattr(exc, "status_code", None)

    if status_code in (429, 500, 502, 503, 504):
        return True

    response = getattr(exc, "response", None)
    response_status = getattr(response, "status_code", None)

    return response_status in (429, 500, 502, 503, 504)
