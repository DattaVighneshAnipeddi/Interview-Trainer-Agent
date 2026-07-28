import json

from app.prompts.evaluation_prompt import EVALUATION_PROMPT
from app.services.gemini_service import ask_gemini


def evaluate_answer(question: str, answer: str):
    """
    Evaluates the candidate's interview answer
    using Gemini AI.
    """

    prompt = EVALUATION_PROMPT.format(
        question=question,
        answer=answer
    )

    response = ask_gemini(prompt)

    # Remove markdown code fences if Gemini returns them
    cleaned_response = (
        response.replace("```json", "")
                .replace("```", "")
                .strip()
    )

    try:
        return json.loads(cleaned_response)

    except json.JSONDecodeError:

        return {
            "overall_score": 0,
            "technical_accuracy": 0,
            "communication": 0,
            "completeness": 0,
            "strengths": "Unable to evaluate.",
            "weaknesses": "Gemini returned invalid JSON.",
            "suggestions": "Please try again.",
            "improved_answer": ""
        }
