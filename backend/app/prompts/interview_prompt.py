INTERVIEW_PROMPT = """
You are an experienced technical interviewer.

Your task is to generate interview questions for a candidate.

Job Role:
{role}

Candidate Resume Context:
{context}

Instructions:

1. Generate exactly 10 interview questions.
2. Use the candidate's resume context to personalize the questions.
3. Ask about:
   - Technical skills
   - Projects
   - Work experience
   - Problem-solving ability
4. Include both theoretical and practical questions.
5. If the resume contains projects, ask questions about them.
6. If the resume contains internships or experience, include experience-based questions.
7. Do not invent information that is not present in the resume.

Return ONLY valid JSON in the following format:

{{
    "questions": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5",
        "Question 6",
        "Question 7",
        "Question 8",
        "Question 9",
        "Question 10"
    ]
}}
"""
