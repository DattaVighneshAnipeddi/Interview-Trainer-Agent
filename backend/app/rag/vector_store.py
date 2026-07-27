import uuid
from typing import Optional

import chromadb

from app.rag.embedding import generate_embedding
from app.schemas.resume import Resume

# Persistent ChromaDB Client
client = chromadb.PersistentClient(path="./chroma_db")

# Resume Collection
collection = client.get_or_create_collection(
    name="resume_collection"
)


def add_resume_chunk(
    chunk_id: str,
    text: str,
    chunk_type: str,
    resume_id: str,
    metadata: Optional[dict] = None,
):
    """
    Store a single resume chunk in ChromaDB.
    """

    embedding = generate_embedding(text)

    chunk_metadata = {
        "resume_id": resume_id,
        "type": chunk_type,
    }

    if metadata:
        chunk_metadata.update(metadata)

    collection.add(
        ids=[chunk_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[chunk_metadata],
    )


def store_resume(resume: Resume):
    """
    Store a parsed resume as semantic chunks.
    Returns the generated resume_id.
    """

    resume_id = str(uuid.uuid4())

    # -------------------------
    # Personal Information
    # -------------------------

    if resume.personal_info.name:

        add_resume_chunk(
            chunk_id=f"{resume_id}_profile",
            text=f"Candidate Name: {resume.personal_info.name}",
            chunk_type="profile",
            resume_id=resume_id,
        )

    # -------------------------
    # Skills
    # -------------------------

    for index, skill in enumerate(resume.skills):

        add_resume_chunk(
            chunk_id=f"{resume_id}_skill_{index}",
            text=skill,
            chunk_type="skill",
            resume_id=resume_id,
        )

    # -------------------------
    # Education
    # -------------------------

    if resume.education:

        education_parts = [
            resume.education.degree,
            resume.education.branch,
            resume.education.graduation_year,
            resume.education.cgpa,
        ]

        education_text = " | ".join(
            str(part)
            for part in education_parts
            if part
        )

        if education_text:

            add_resume_chunk(
                chunk_id=f"{resume_id}_education",
                text=education_text,
                chunk_type="education",
                resume_id=resume_id,
            )

    # -------------------------
    # Projects
    # -------------------------

    for index, project in enumerate(resume.projects):

        project_text = (
            f"{project.title}. "
            f"{project.description}"
        )

        add_resume_chunk(
            chunk_id=f"{resume_id}_project_{index}",
            text=project_text,
            chunk_type="project",
            resume_id=resume_id,
        )

    # -------------------------
    # Experience
    # -------------------------

    for index, experience in enumerate(resume.experience):

        experience_parts = [
            experience.role,
            experience.company,
            experience.duration,
        ]

        experience_text = " | ".join(
            str(part)
            for part in experience_parts
            if part
        )

        add_resume_chunk(
            chunk_id=f"{resume_id}_experience_{index}",
            text=experience_text,
            chunk_type="experience",
            resume_id=resume_id,
        )

    # -------------------------
    # Certifications
    # -------------------------

    for index, certification in enumerate(resume.certifications):

        add_resume_chunk(
            chunk_id=f"{resume_id}_certification_{index}",
            text=certification,
            chunk_type="certification",
            resume_id=resume_id,
        )

    return resume_id
