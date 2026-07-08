import re


def extract_resume_info(text: str):
    """
    Extract basic information from resume text.
    """

    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else None

    # Phone Number
    phone_match = re.search(r'(\+?\d[\d\s-]{8,}\d)', text)
    phone = phone_match.group(0) if phone_match else None

    # Name (Assume first non-empty line)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    name = lines[0] if lines else None

    return {
        "name": name,
        "email": email,
        "phone": phone
    }
