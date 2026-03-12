from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from apps.backend.llm_provider import LLMResponse, ToolCall
from apps.backend.models import CreateBlockInput, EvaluationResponse

pytestmark = pytest.mark.anyio


def _make_provider(responses: list[LLMResponse]) -> MagicMock:
    """Create a mock provider that returns the given LLMResponse sequence."""
    provider = MagicMock()
    provider.create = AsyncMock(side_effect=responses)
    provider.build_result_messages = MagicMock(return_value=[])
    provider.is_rate_limit_error = MagicMock(return_value=False)
    return provider


async def test_create_blocks_returns_blocks():
    """create_blocks should collect CreateBlockInput from tool calls."""
    resp = LLMResponse(
        tool_calls=[
            ToolCall(
                id="call_1",
                name="create_block",
                input={"content": "Block one content.", "questions": ["Q1?", "Q2?"]},
            )
        ],
        is_done=True,
        _raw=None,
    )
    provider = _make_provider([resp])

    with patch("apps.backend.llm_service._get_provider", return_value=provider):
        from apps.backend.llm_service import create_blocks

        blocks = await create_blocks("Block one content.", num_questions=2)

    assert len(blocks) == 1
    assert isinstance(blocks[0], CreateBlockInput)
    assert blocks[0].content == "Block one content."
    assert blocks[0].questions == ["Q1?", "Q2?"]


async def test_create_blocks_multiple_turns():
    """create_blocks should loop until the model stops calling tools."""
    resp1 = LLMResponse(
        tool_calls=[
            ToolCall(
                id="call_1",
                name="create_block",
                input={"content": "Block A.", "questions": ["QA?"]},
            )
        ],
        is_done=False,
        _raw=None,
    )
    resp2 = LLMResponse(
        tool_calls=[
            ToolCall(
                id="call_2",
                name="create_block",
                input={"content": "Block B.", "questions": ["QB?"]},
            )
        ],
        is_done=True,
        _raw=None,
    )
    provider = _make_provider([resp1, resp2])

    with patch("apps.backend.llm_service._get_provider", return_value=provider):
        from apps.backend.llm_service import create_blocks

        blocks = await create_blocks("Block A.\n\nBlock B.", num_questions=1)

    assert len(blocks) == 2
    assert blocks[0].content == "Block A."
    assert blocks[1].content == "Block B."
    assert provider.create.await_count == 2


async def test_generate_questions_returns_list():
    """generate_questions should extract questions from the tool response."""
    resp = LLMResponse(
        tool_calls=[
            ToolCall(
                id="call_1",
                name="return_questions",
                input={"questions": ["New Q1?", "New Q2?"]},
            )
        ],
        is_done=True,
        _raw=None,
    )
    provider = _make_provider([resp])

    with patch("apps.backend.llm_service._get_provider", return_value=provider):
        from apps.backend.llm_service import generate_questions

        questions = await generate_questions("Some content.", 2)

    assert questions == ["New Q1?", "New Q2?"]


async def test_evaluate_answer_returns_evaluation():
    """evaluate_answer should return an EvaluationResponse."""
    resp = LLMResponse(
        tool_calls=[
            ToolCall(
                id="call_1",
                name="return_evaluation",
                input={"score": 90, "feedback": "Excellent."},
            )
        ],
        is_done=True,
        _raw=None,
    )
    provider = _make_provider([resp])

    with patch("apps.backend.llm_service._get_provider", return_value=provider):
        from apps.backend.llm_service import evaluate_answer

        result = await evaluate_answer("Q?", "A.", "Context.")

    assert isinstance(result, EvaluationResponse)
    assert result.score == 90
    assert result.feedback == "Excellent."
