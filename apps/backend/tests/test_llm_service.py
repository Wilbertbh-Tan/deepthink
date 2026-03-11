from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from apps.backend.models import CreateBlockInput, EvaluationResponse

pytestmark = pytest.mark.anyio


async def test_create_blocks_returns_blocks():
    """create_blocks should collect CreateBlockInput from tool calls."""
    # Build a fake response with one tool_use content block
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "create_block"
    tool_block.id = "call_1"
    tool_block.input = {
        "content": "Block one content.",
        "questions": ["Q1?", "Q2?"],
    }

    response = MagicMock()
    response.content = [tool_block]
    response.stop_reason = "end_turn"

    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=response)

    with patch("apps.backend.llm_service._get_client", return_value=mock_client):
        from apps.backend.llm_service import create_blocks

        blocks = await create_blocks("Block one content.", num_questions=2)

    assert len(blocks) == 1
    assert isinstance(blocks[0], CreateBlockInput)
    assert blocks[0].content == "Block one content."
    assert blocks[0].questions == ["Q1?", "Q2?"]


async def test_create_blocks_multiple_turns():
    """create_blocks should loop until the model stops calling tools."""
    # First response: tool call, stop_reason = "tool_use"
    tool_block_1 = MagicMock()
    tool_block_1.type = "tool_use"
    tool_block_1.name = "create_block"
    tool_block_1.id = "call_1"
    tool_block_1.input = {"content": "Block A.", "questions": ["QA?"]}

    resp1 = MagicMock()
    resp1.content = [tool_block_1]
    resp1.stop_reason = "tool_use"

    # Second response: another tool call, stop_reason = "end_turn"
    tool_block_2 = MagicMock()
    tool_block_2.type = "tool_use"
    tool_block_2.name = "create_block"
    tool_block_2.id = "call_2"
    tool_block_2.input = {"content": "Block B.", "questions": ["QB?"]}

    resp2 = MagicMock()
    resp2.content = [tool_block_2]
    resp2.stop_reason = "end_turn"

    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(side_effect=[resp1, resp2])

    with patch("apps.backend.llm_service._get_client", return_value=mock_client):
        from apps.backend.llm_service import create_blocks

        blocks = await create_blocks("Block A.\n\nBlock B.", num_questions=1)

    assert len(blocks) == 2
    assert blocks[0].content == "Block A."
    assert blocks[1].content == "Block B."
    assert mock_client.messages.create.await_count == 2


async def test_generate_questions_returns_list():
    """generate_questions should extract questions from the tool response."""
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "return_questions"
    tool_block.input = {"questions": ["New Q1?", "New Q2?"]}

    response = MagicMock()
    response.content = [tool_block]

    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=response)

    with patch("apps.backend.llm_service._get_client", return_value=mock_client):
        from apps.backend.llm_service import generate_questions

        questions = await generate_questions("Some content.", 2)

    assert questions == ["New Q1?", "New Q2?"]


async def test_evaluate_answer_returns_evaluation():
    """evaluate_answer should return an EvaluationResponse."""
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "return_evaluation"
    tool_block.input = {"score": 90, "feedback": "Excellent."}

    response = MagicMock()
    response.content = [tool_block]

    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=response)

    with patch("apps.backend.llm_service._get_client", return_value=mock_client):
        from apps.backend.llm_service import evaluate_answer

        result = await evaluate_answer("Q?", "A.", "Context.")

    assert isinstance(result, EvaluationResponse)
    assert result.score == 90
    assert result.feedback == "Excellent."
