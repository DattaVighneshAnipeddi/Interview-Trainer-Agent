import re
from app.schemas.resume import PersonalInfo


def extract_resume_info(text: str):

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else None

    phone_match = re.search(r'(\+?\d[\d\s-]{8,}\d)', text)
    phone = phone_match.group(0) if phone_match else None

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    name = lines[0] if lines else None

    return PersonalInfo(
        name=name,
        email=email,
        phone=phone
    )
