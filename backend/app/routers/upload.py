
import logging
import os
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.resume import Resume
from app.services.resume_processor import process_resume
from app.services.gemini_service import (
    GeminiQuotaExceeded,
    GeminiServiceUnavailable,
)


logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume", response_model=Resume)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid PDF resume.",
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        os.path.basename(file.filename),
    )

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        resume = process_resume(file_path)
        return resume

    except GeminiQuotaExceeded as exc:
        logger.warning("Resume processing stopped due to Gemini quota limits.")
        raise HTTPException(
            status_code=429,
            detail=str(exc),
        ) from exc

    except GeminiServiceUnavailable as exc:
        logger.warning(
            "Resume processing stopped because Gemini is unavailable.")
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Resume upload failed.")
        raise HTTPException(
            status_code=500,
            detail="Resume processing failed due to an internal error.",
        ) from exc

    finally:
        await file.close()
