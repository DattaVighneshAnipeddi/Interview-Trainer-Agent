from app.prompts.interview_prompt import INTERVIEW_PROMPT
from app.rag.retriever import retrieve_context
from app.services.gemini_service import ask_gemini


def generate_interview_questions(role: str):
    """
    Generate personalized interview questions based on
    the candidate's resume and target job role.
    """

    retrieval_result = retrieve_context(role)

    documents = retrieval_result["documents"]
    metadata = retrieval_result["metadata"]

    context_parts = []

    for doc, meta in zip(documents, metadata):
        chunk_type = meta.get("type", "Unknown").capitalize()
        context_parts.append(f"[{chunk_type}]\n{doc}")

    context = "\n\n".join(context_parts)

    prompt = INTERVIEW_PROMPT.format(
        role=role,
        context=context
    )

    response = ask_gemini(prompt)
    questions = re.split(r"\n\d+\.\s*", response.strip())

    questions = [q.strip() for q in questions if q.strip()]

    return questions

    return response
