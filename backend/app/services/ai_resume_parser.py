import json

from app.prompts.resume_prompt import RESUME_PARSER_PROMPT
from app.services.gemini_service import ask_gemini


def parse_resume_with_ai(resume_text: str):
    prompt = RESUME_PARSER_PROMPT.format(
        resume=resume_text
    )

    response = ask_gemini(prompt)

    # Remove markdown if Gemini returns ```json ... ```
    cleaned = response.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError as e:
        print(f"Gemini JSON parsing failed: {e}")

        return {
            "projects": [],
            "experience": [],
            "certifications": []
        }
