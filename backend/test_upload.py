from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth_dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.services.gemini_service import (
    GeminiQuotaExceeded,
    GeminiServiceUnavailable,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_dependency_overrides():
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides.pop(get_current_user, None)

    try:
        yield
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture
def authenticated_client():
    original_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[get_current_user] = (
        lambda: UserResponse(
            user_id=1,
            name="Test User",
            email="test@example.com",
            role="user",
        )
    )

    try:
        yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


def valid_pdf():
    # The upload endpoint checks the PDF signature before processing.
    return b"%PDF-1.4 test content"


def test_upload_requires_authentication():
    response = client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", valid_pdf(), "application/pdf")},
    )

    assert response.status_code == 401


def test_invalid_file_type(authenticated_client):
    response = authenticated_client.post(
        "/upload-resume",
        files={"file": ("resume.txt", b"Not a PDF", "text/plain")},
    )

    assert response.status_code == 400


def test_invalid_pdf_content(authenticated_client):
    response = authenticated_client.post(
        "/upload-resume",
        files={
            "file": (
                "resume.pdf",
                b"This is not a PDF",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400


def test_oversized_upload_is_rejected(authenticated_client):
    response = authenticated_client.post(
        "/upload-resume",
        files={
            "file": (
                "resume.pdf",
                b"%PDF-" + b"x" * (5 * 1024 * 1024),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413


def test_quota_exceeded(authenticated_client):
    with patch(
        "app.routers.upload.process_resume",
        side_effect=GeminiQuotaExceeded("Test quota exceeded"),
    ):
        response = authenticated_client.post(
            "/upload-resume",
            files={
                "file": (
                    "resume.pdf",
                    valid_pdf(),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 429


def test_gemini_unavailable(authenticated_client):
    with patch(
        "app.routers.upload.process_resume",
        side_effect=GeminiServiceUnavailable("Test service unavailable"),
    ):
        response = authenticated_client.post(
            "/upload-resume",
            files={
                "file": (
                    "resume.pdf",
                    valid_pdf(),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 503


def test_temporary_file_is_removed_after_processing(authenticated_client):
    captured_paths = []

    def fake_process_resume(file_path):
        captured_paths.append(file_path)
        assert Path(file_path).exists()
        raise GeminiServiceUnavailable("Simulated failure")

    with patch(
        "app.routers.upload.process_resume",
        side_effect=fake_process_resume,
    ):
        response = authenticated_client.post(
            "/upload-resume",
            files={
                "file": (
                    "resume.pdf",
                    valid_pdf(),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 503
    assert len(captured_paths) == 1
    assert not Path(captured_paths[0]).exists()
