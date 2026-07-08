TECHNICAL_SKILLS = [
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "TypeScript",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Express",
    "FastAPI",
    "Flask",
    "Django",
    "HTML",
    "CSS",
    "Bootstrap",
    "Tailwind CSS",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Git",
    "GitHub",
    "Docker",
    "Kubernetes",
    "Linux",
    "AWS",
    "Azure",
    "GCP",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Pandas",
    "NumPy",
    "OpenCV",
    "LangChain",
    "ChromaDB"
]


def extract_skills(text: str):
    extracted_skills = []

    text_lower = text.lower()

    for skill in TECHNICAL_SKILLS:
        if skill.lower() in text_lower:
            extracted_skills.append(skill)

    return sorted(list(set(extracted_skills)))