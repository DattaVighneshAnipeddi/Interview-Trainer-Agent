
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.gemini_service import (
    GeminiQuotaExceeded,
    GeminiServiceUnavailable,
)

client = TestClient(app)


def test_quota_exceeded():
    with patch(
        "app.routers.upload.process_resume",
        side_effect=GeminiQuotaExceeded("Test quota exceeded"),
    ):
        response = client.post(
            "/upload-resume",
            files={
                "file": (
                    "resume.pdf",
                    b"%PDF-1.4 test content",
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 429, response.text
    print("PASS: Upload returns HTTP 429 for Gemini quota errors.")


def test_gemini_unavailable():
    with patch(
        "app.routers.upload.process_resume",
        side_effect=GeminiServiceUnavailable("Test service unavailable"),
    ):
        response = client.post(
            "/upload-resume",
            files={
                "file": (
                    "resume.pdf",
                    b"%PDF-1.4 test content",
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 503, response.text
    print("PASS: Upload returns HTTP 503 for Gemini service failures.")


def test_invalid_file_type():
    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "resume.txt",
                b"Not a PDF",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400, response.text
    print("PASS: Upload rejects non-PDF filenames.")


if __name__ == "__main__":
    test_quota_exceeded()
    test_gemini_unavailable()
    test_invalid_file_type()
    print("\nAll upload endpoint tests passed!")
