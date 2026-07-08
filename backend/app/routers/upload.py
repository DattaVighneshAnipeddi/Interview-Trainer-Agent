from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.services.resume_parser import extract_text_from_pdf
from app.services.resume_extractor import extract_resume_info

router = APIRouter()

UPLOAD_DIR = "app/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_pdf(file_path)

    resume_info = extract_resume_info(extracted_text)

    return {
        "filename": file.filename,
        "message": "Resume uploaded and parsed successfully!",
        "resume_info": resume_info,
        "text": extracted_text
    }
