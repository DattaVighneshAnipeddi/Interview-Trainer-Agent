from app.schemas.report import InterviewReport, QuestionReport
from app.services.session_service import get_session


def generate_interview_report(
    session_id: str,
    user_id: int,
) -> InterviewReport:
    """Generate a report only for a session owned by the user."""

    # Retrieve the session only if it belongs to this user.
    session = get_session(session_id, user_id)

    if session is None:
        raise ValueError("Interview session not found")

    # Only generate a final report for completed interviews.
    if session.current_question < len(session.questions):
        raise ValueError("Interview session is not yet completed")

    responses = session.responses

    if not responses:
        raise ValueError("No interview responses are available")

    # Calculate average scores.
    total_responses = len(responses)

    overall_score = sum(
        response.evaluation.overall_score
        for response in responses
    ) / total_responses

    average_technical_accuracy = sum(
        response.evaluation.technical_accuracy
        for response in responses
    ) / total_responses

    average_communication = sum(
        response.evaluation.communication
        for response in responses
    ) / total_responses

    average_completeness = sum(
        response.evaluation.completeness
        for response in responses
    ) / total_responses

    # Collect question-by-question feedback.
    question_reports = []

    for response in responses:
        evaluation = response.evaluation

        question_reports.append(
            QuestionReport(
                question=response.question,
                answer=response.answer,
                score=evaluation.overall_score,
                technical_accuracy=evaluation.technical_accuracy,
                communication=evaluation.communication,
                completeness=evaluation.completeness,
                strengths=evaluation.strengths,
                weaknesses=evaluation.weaknesses,
                suggestions=evaluation.suggestions,
            )
        )

    # Collect strengths, weaknesses, and recommendations.
    strengths = list(dict.fromkeys(
        response.evaluation.strengths
        for response in responses
        if response.evaluation.strengths.strip()
    ))

    weaknesses = list(dict.fromkeys(
        response.evaluation.weaknesses
        for response in responses
        if response.evaluation.weaknesses.strip()
    ))

    recommendations = list(dict.fromkeys(
        response.evaluation.suggestions
        for response in responses
        if response.evaluation.suggestions.strip()
    ))

    # Build the final report.
    return InterviewReport(
        session_id=session.session_id,
        role=session.role,
        total_questions=len(session.questions),
        answered_questions=total_responses,
        overall_score=round(overall_score, 2),
        average_technical_accuracy=round(
            average_technical_accuracy, 2
        ),
        average_communication=round(
            average_communication, 2
        ),
        average_completeness=round(
            average_completeness, 2
        ),
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        question_reports=question_reports,
    )
