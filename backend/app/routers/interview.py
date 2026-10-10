from app.services.report_service import generate_interview_report
from app.services.session_service import (
    create_session,
    get_session,
    submit_answer,
)
from app.services.interview_service import generate_interview_questions
from app.services.evaluation_service import evaluate_answer
from app.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.schemas.interview import InterviewQuestionsResponse
from app.schemas.evaluation import EvaluationResult
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


# -----------------------------
# Request Models
# -----------------------------

class InterviewRequest(BaseModel):
    role: str = Field(min_length=1)


class EvaluationRequest(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


# -----------------------------
# Generate Interview Questions
# -----------------------------

@router.post(
    "/questions",
    response_model=InterviewQuestionsResponse
)
def generate_questions(request: InterviewRequest):

    role = request.role.strip()

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Role cannot be empty"
        )

    try:
        result = generate_interview_questions(role)

        return InterviewQuestionsResponse(
            role=role,
            questions=result.questions
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate interview questions: {str(e)}"
        )


# -----------------------------
# Create Interview Session
# -----------------------------

@router.post(
    "/session",
    response_model=CreateSessionResponse
)
def start_session(request: CreateSessionRequest):

    role = request.role.strip()

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Role cannot be empty"
        )

    try:
        result = generate_interview_questions(role)

        if not result.questions:
            raise HTTPException(
                status_code=500,
                detail="No interview questions were generated"
            )

        session = create_session(
            role=role,
            questions=result.questions
        )

        return CreateSessionResponse(
            session_id=session.session_id,
            role=session.role,
            current_question=session.questions[0],
            total_questions=len(session.questions)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


# -----------------------------
# Submit Interview Answer
# -----------------------------

@router.post(
    "/session/{session_id}/answer",
    response_model=SubmitAnswerResponse
)
def submit_interview_answer(
    session_id: str,
    request: SubmitAnswerRequest
):

    # Find the interview session
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )

    # Check if interview is already completed
    if session.current_question >= len(session.questions):
        raise HTTPException(
            status_code=400,
            detail="Interview session is already completed"
        )

    # Validate the candidate's answer
    answer = request.answer.strip()

    if not answer:
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty"
        )

    # Get the current question
    current_question = session.questions[
        session.current_question
    ]

    try:
        # Evaluate the candidate's answer
        evaluation = evaluate_answer(
            current_question,
            answer
        )

        # Store the question, answer, and evaluation
        updated_session = submit_answer(
            session_id,
            answer,
            evaluation
        )

        # Check whether the interview is completed
        interview_completed = (
            updated_session.current_question
            >= len(updated_session.questions)
        )

        # Determine the next question and remaining count
        if interview_completed:
            next_question = None
            remaining_questions = 0

        else:
            next_question = updated_session.questions[
                updated_session.current_question
            ]

            remaining_questions = (
                len(updated_session.questions)
                - updated_session.current_question
            )

        return SubmitAnswerResponse(
            evaluation=evaluation,
            next_question=next_question,
            remaining_questions=remaining_questions,
            interview_completed=interview_completed
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit answer: {str(e)}"
        )


# -----------------------------
# Standalone Answer Evaluation
# -----------------------------

@router.post(
    "/evaluate",
    response_model=EvaluationResult
)
def evaluate(request: EvaluationRequest):

    question = request.question.strip()
    answer = request.answer.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    if not answer:
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty"
        )

    try:
        result = evaluate_answer(
            question,
            answer
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate answer: {str(e)}"
        )

# -----------------------------
# Final Interview Report
# -----------------------------


@router.get(
    "/session/{session_id}/report"
)
def get_interview_report(session_id: str):

    try:
        report = generate_interview_report(session_id)
        return report

    except ValueError as e:
        message = str(e)

        if message == "Interview session not found":
            status_code = 404
        elif message == "Interview session is not yet completed":
            status_code = 400
        elif message == "No interview responses are available":
            status_code = 400
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate interview report: {str(e)}"
        )
