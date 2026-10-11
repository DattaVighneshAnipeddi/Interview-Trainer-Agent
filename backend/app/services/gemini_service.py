
import logging
import random
import time

from google import genai
from google.genai import errors, types

from app.config import GEMINI_API_KEY


logger = logging.getLogger(__name__)


class GeminiServiceUnavailable(Exception):
    """Raised when Gemini remains unavailable after retries."""


class GeminiQuotaExceeded(Exception):
    """Raised when Gemini's API quota or rate limit is exceeded."""


client = genai.Client(api_key=GEMINI_API_KEY)

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0
MAX_RETRY_DELAY = 8.0


def is_retryable_error(exc: Exception) -> bool:
    """Return True only for temporary errors worth retrying."""

    if isinstance(exc, errors.APIError):
        return exc.code in (500, 502, 503, 504)

    status_code = getattr(exc, "status_code", None)

    if status_code in (500, 502, 503, 504):
        return True

    response = getattr(exc, "response", None)
    response_status = getattr(response, "status_code", None)

    return response_status in (500, 502, 503, 504)


def ask_gemini(prompt: str, response_schema=None):
    """Send a prompt to Gemini with retry handling for temporary failures."""

    config = None

    if response_schema is not None:
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

            if response_schema is not None:
                if response.parsed is None:
                    raise ValueError(
                        "Gemini returned no structured response."
                    )
                return response.parsed

            if response.text is None:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            return response.text

        except Exception as exc:
            # Quota/rate-limit errors must not be retried here.
            if isinstance(exc, errors.APIError) and exc.code == 429:
                raise GeminiQuotaExceeded(
                    "Gemini API quota or rate limit exceeded. "
                    "Please try again later or check your API quota."
                ) from exc

            # Do not retry authentication, invalid requests, or other
            # errors that are not classified as temporary.
            if not is_retryable_error(exc):
                logger.exception("Gemini request failed.")
                raise

            # Three retries means a maximum of four total attempts.
            if attempt == MAX_RETRIES:
                logger.error(
                    "Gemini retries exhausted after %s attempts.",
                    attempt + 1,
                    exc_info=True,
                )
                raise GeminiServiceUnavailable(
                    "Gemini is temporarily unavailable. "
                    "Please try again later."
                ) from exc

        # Reached only after a retryable failure with attempts remaining.
        delay = min(
            INITIAL_RETRY_DELAY * (2 ** attempt),
            MAX_RETRY_DELAY,
        )
        delay += random.uniform(0, 0.25)

        logger.warning(
            "Temporary Gemini failure. Retrying in %.2f seconds "
            "(attempt %s of %s).",
            delay,
            attempt + 1,
            MAX_RETRIES,
        )

        time.sleep(delay)
