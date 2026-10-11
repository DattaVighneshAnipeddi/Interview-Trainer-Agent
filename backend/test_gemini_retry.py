
from unittest.mock import MagicMock, patch

from google.genai import errors

from app.services.gemini_service import (
    ask_gemini,
    is_retryable_error,
    GeminiServiceUnavailable,
    GeminiQuotaExceeded,
)


def make_error(code):
    return errors.APIError(
        code=code,
        response_json={"error": {"message": "Test error"}},
    )


def test_retryable_errors():
    for code in (500, 502, 503, 504):
        assert is_retryable_error(make_error(code)) is True

    for code in (400, 401, 403, 404, 429):
        assert is_retryable_error(make_error(code)) is False

    print("PASS: Retryable and non-retryable errors classified correctly.")


def test_retry_then_success():
    mock_response = MagicMock()
    mock_response.text = "Python is a programming language."

    with (
        patch(
            "app.services.gemini_service.client.models.generate_content",
            side_effect=[make_error(503), mock_response],
        ) as mock_generate,
        patch("app.services.gemini_service.time.sleep") as mock_sleep,
        patch(
            "app.services.gemini_service.random.uniform",
            return_value=0,
        ),
    ):
        result = ask_gemini("Explain Python")

        assert result == "Python is a programming language."
        assert mock_generate.call_count == 2
        assert mock_sleep.call_count == 1

    print("PASS: Gemini retried after HTTP 503 and then succeeded.")


def test_retries_exhausted():
    with (
        patch(
            "app.services.gemini_service.client.models.generate_content",
            side_effect=make_error(503),
        ) as mock_generate,
        patch("app.services.gemini_service.time.sleep"),
        patch(
            "app.services.gemini_service.random.uniform",
            return_value=0,
        ),
    ):
        try:
            ask_gemini("Explain Python")
        except GeminiServiceUnavailable:
            assert mock_generate.call_count == 4
        else:
            raise AssertionError("Expected GeminiServiceUnavailable")

    print("PASS: Service unavailable raised after four attempts.")


def test_quota_exceeded():
    with (
        patch(
            "app.services.gemini_service.client.models.generate_content",
            side_effect=make_error(429),
        ) as mock_generate,
        patch("app.services.gemini_service.time.sleep") as mock_sleep,
    ):
        try:
            ask_gemini("Explain Python")
        except GeminiQuotaExceeded:
            assert mock_generate.call_count == 1
            mock_sleep.assert_not_called()
        else:
            raise AssertionError("Expected GeminiQuotaExceeded")

    print("PASS: HTTP 429 raised quota exception without retrying.")


if __name__ == "__main__":
    test_retryable_errors()
    test_retry_then_success()
    test_retries_exhausted()
    test_quota_exceeded()

    print("\nAll Gemini retry tests passed!")
