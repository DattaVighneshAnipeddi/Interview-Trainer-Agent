RESUME_PARSER_PROMPT = """
You are an expert AI Resume Parser.

Analyze the following resume.

Extract the following information and return ONLY valid JSON.

{{
    "projects": [
        {{
            "title": "",
            "description": ""
        }}
    ],
    "experience": [
        {{
            "company": "",
            "role": "",
            "duration": ""
        }}
    ],
    "certifications": []
}}

Resume:

{resume}
"""