import re

DEGREES = [
    "Bachelor of Technology",
    "B.Tech",
    "Bachelor of Engineering",
    "B.E",
    "Master of Technology",
    "M.Tech",
    "Master of Science",
    "M.Sc",
    "Bachelor of Science",
    "B.Sc",
    "Master of Computer Applications",
    "MCA",
    "Bachelor of Computer Applications",
    "BCA",
    "MBA",
    "Diploma"
]

BRANCHES = [
    "Computer Science",
    "Computer Science and Engineering",
    "Computer Science & Engineering",
    "Computer Science and Systems Engineering",
    "Computer Science & Systems Engineering",
    "Information Technology",
    "Artificial Intelligence",
    "Artificial Intelligence and Machine Learning",
    "Electronics and Communication Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Data Science"
]


def extract_education(text: str):
    """
    Extract education details from resume text.
    """

    education = {
        "degree": None,
        "branch": None,
        "cgpa": None,
        "graduation_year": None
    }

    # Degree
    for degree in DEGREES:
        if degree.lower() in text.lower():
            education["degree"] = degree
            break

    # Branch
    for branch in BRANCHES:
        if branch.lower() in text.lower():
            education["branch"] = branch
            break

    # CGPA
    cgpa_match = re.search(r'CGPA[:\s]*([0-9]\.?[0-9]*)', text, re.IGNORECASE)

    if cgpa_match:
        education["cgpa"] = cgpa_match.group(1)

    # Graduation Year
    year_match = re.search(r'(20[2-5][0-9])', text)

    if year_match:
        education["graduation_year"] = year_match.group(1)

    return education
