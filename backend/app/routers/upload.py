from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.services.resume_processor import process_resume

router = APIRouter()

UPLOAD_DIR = "app/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume = process_resume(file_path)

    return {
        "filename": file.filename,
        "message": "Resume uploaded and processed successfully!",
        "resume": resume
    }
