from app.rag.vector_store import store_resume
from app.services.ai_resume_parser import parse_resume_with_ai
from app.services.resume_parser import extract_text_from_pdf
from app.services.resume_extractor import extract_resume_info
from app.services.skill_extractor import extract_skills
from app.services.education_extractor import extract_education
from app.schemas.resume import Resume


def process_resume(file_path: str):

    text = extract_text_from_pdf(file_path)

    ai_data = parse_resume_with_ai(text)

    resume = Resume(
        personal_info=extract_resume_info(text),
        skills=extract_skills(text),
        education=extract_education(text),
        projects=ai_data.get("projects", []),
        experience=ai_data.get("experience", []),
        certifications=ai_data.get("certifications", []),
        raw_text=text,
    )

    resume_id = store_resume(resume)

    print(f"Resume stored successfully: {resume_id}")

    return resume
