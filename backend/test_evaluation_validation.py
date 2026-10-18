
import pytest
from pydantic import ValidationError

from app.schemas.evaluation import EvaluationResult


def valid_evaluation():
    return {
        "overall_score": 8.5,
        "technical_accuracy": 9,
        "communication": 8,
        "completeness": 8,
        "strengths": "Good technical understanding",
        "weaknesses": "Needs more examples",
        "suggestions": "Include practical examples",
        "improved_answer": "A clearer and more complete answer",
    }


def test_valid_evaluation_is_accepted():
    result = EvaluationResult(**valid_evaluation())
    assert result.overall_score == 8.5


@pytest.mark.parametrize(
    "field,value",
    [
        ("overall_score", -1),
        ("overall_score", 10.1),
        ("technical_accuracy", -1),
        ("technical_accuracy", 11),
        ("communication", 11),
        ("completeness", -1),
    ],
)
def test_invalid_scores_are_rejected(field, value):
    data = valid_evaluation()
    data[field] = value

    with pytest.raises(ValidationError):
        EvaluationResult(**data)


@pytest.mark.parametrize(
    "field",
    ["strengths", "weaknesses", "suggestions", "improved_answer"],
)
def test_empty_feedback_is_rejected(field):
    data = valid_evaluation()
    data[field] = ""

    with pytest.raises(ValidationError):
        EvaluationResult(**data)
