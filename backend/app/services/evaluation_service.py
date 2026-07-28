from app.prompts.evaluation_prompt import EVALUATION_PROMPT
from app.schemas.evaluation import EvaluationResult
from app.services.gemini_service import ask_gemini


def evaluate_answer(question: str, answer: str) -> EvaluationResult:
    prompt = EVALUATION_PROMPT.format(
        question=question,
        answer=answer
    )

    result = ask_gemini(
        prompt,
        response_schema=EvaluationResult
    )

    return result
