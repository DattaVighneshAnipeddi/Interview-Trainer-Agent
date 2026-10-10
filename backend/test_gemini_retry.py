from unittest.mock import patch, MagicMock

from google.genai import errors

from app.services.gemini_service import (
    ask_gemini,
    GeminiServiceUnavailable,
)


def make_error(code):
    return errors.APIError(
        code=code,
        response_json={"error": {"message": "Test error"}},
    )


def test_retry_then_success():
    mock_response = MagicMock()
    mock_response.text = "Python is a programming language."

    with (
        patch(
            "app.services.gemini_service.client.models.generate_content",
            side_effect=[
                make_error(503),
                mock_response,
            ],
        ) as mock_generate,
        patch("app.services.gemini_service.time.sleep"),
        patch("app.services.gemini_service.random.uniform", return_value=0),
    ):
        result = ask_gemini("Explain Python")

        assert result == "Python is a programming language."
        assert mock_generate.call_count == 2

    print("PASS: Gemini retried after HTTP 503 and then succeeded.")


def test_retries_exhausted():
    with (
        patch(
            "app.services.gemini_service.client.models.generate_content",
            side_effect=make_error(503),
        ) as mock_generate,
        patch("app.services.gemini_service.time.sleep"),
        patch("app.services.gemini_service.random.uniform", return_value=0),
    ):
        try:
            ask_gemini("Explain Python")
        except GeminiServiceUnavailable:
            assert mock_generate.call_count == 4
            print("PASS: GeminiServiceUnavailable raised after 4 attempts.")
        else:
            raise AssertionError("Expected GeminiServiceUnavailable")


if __name__ == "__main__":
    test_retry_then_success()
    test_retries_exhausted()
    print("\nAll retry loop tests passed!")
