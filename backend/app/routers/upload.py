
import logging
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth_dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.resume import Resume
from app.services.resume_processor import process_resume
from app.services.gemini_service import (
    GeminiQuotaExceeded,
    GeminiServiceUnavailable,
)

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
CHUNK_SIZE = 64 * 1024  # 64 KB


@router.post("/upload-resume", response_model=Resume)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid PDF resume.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            prefix="resume_",
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            total_size = 0

            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Resume file exceeds the 5 MB limit.",
                    )

                temp_file.write(chunk)

        with open(temp_path, "rb") as pdf_file:
            if pdf_file.read(5) != b"%PDF-":
                raise HTTPException(
                    status_code=400,
                    detail="The uploaded file is not a valid PDF.",
                )

        resume = process_resume(temp_path)
        return resume

    except HTTPException:
        raise

    except GeminiQuotaExceeded as exc:
        logger.warning("Resume processing stopped due to Gemini quota limits.")
        raise HTTPException(
            status_code=429,
            detail="AI processing quota exceeded. Please try again later.",
        ) from exc

    except GeminiServiceUnavailable as exc:
        logger.warning("Resume processing stopped because Gemini is unavailable.")
        raise HTTPException(
            status_code=503,
            detail="AI processing is temporarily unavailable.",
        ) from exc

    except Exception as exc:
        logger.exception("Resume upload failed.")
        raise HTTPException(
            status_code=500,
            detail="Resume processing failed due to an internal error.",
        ) from exc

    finally:
        await file.close()

        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                logger.exception("Failed to delete temporary resume file.")
