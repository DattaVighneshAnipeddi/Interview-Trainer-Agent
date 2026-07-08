from app.services.resume_parser import extract_text_from_pdf
from app.services.resume_extractor import extract_resume_info
from app.services.skill_extractor import extract_skills
from app.services.education_extractor import extract_education
from app.schemas.resume import Resume


def process_resume(file_path: str):
    """
    Process a resume PDF and return structured information.
    """

    text = extract_text_from_pdf(file_path)

    resume = Resume(
        personal_info=extract_resume_info(text),
        skills=extract_skills(text),
        education=extract_education(text),
        raw_text=text
    )

    return resume
