from app.prompts.interview_prompt import INTERVIEW_PROMPT
from app.rag.retriever import retrieve_context
from app.schemas.interview import InterviewQuestions
from app.services.gemini_service import ask_gemini


def generate_interview_questions(role: str):

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

    result = ask_gemini(
        prompt,
        response_schema=InterviewQuestions
    )

    return result
