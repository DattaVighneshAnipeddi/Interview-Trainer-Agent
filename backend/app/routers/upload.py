from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.schemas.resume import Resume
from app.services.resume_processor import process_resume

router = APIRouter()

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume", response_model=Resume)
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume = process_resume(file_path)

    return resume
