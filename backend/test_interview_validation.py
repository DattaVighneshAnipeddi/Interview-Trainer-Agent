
import pytest
from pydantic import ValidationError

from app.schemas.session import CreateSessionRequest, SubmitAnswerRequest


@pytest.mark.parametrize("role", ["", " ", "   ", "A"])
def test_create_session_rejects_invalid_role(role):
    with pytest.raises(ValidationError):
        CreateSessionRequest(role=role)


def test_create_session_trims_role():
    request = CreateSessionRequest(role="  Python Developer  ")
    assert request.role == "Python Developer"


@pytest.mark.parametrize("answer", ["", " ", "   "])
def test_submit_answer_rejects_empty_answer(answer):
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(answer=answer)


def test_submit_answer_trims_surrounding_whitespace():
    request = SubmitAnswerRequest(answer="  My answer  ")
    assert request.answer == "My answer"


def test_submit_answer_rejects_answer_over_limit():
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(answer="a" * 10001)
