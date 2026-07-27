from app.prompts.interview_prompt import INTERVIEW_PROMPT
from app.rag.retriever import retrieve_context
from app.services.gemini_service import ask_gemini


def generate_interview_questions(role: str):

    context = retrieve_context(role)

    prompt = INTERVIEW_PROMPT.format(
        role=role,
        context="\n".join(context)
    )

    response = ask_gemini(prompt)

    return response