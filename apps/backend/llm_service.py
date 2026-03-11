import asyncio
import random
from functools import lru_cache
from pathlib import Path

import anthropic

from .config import get_settings
from .models import CreateBlockInput, EvaluationResponse, QuestionsResponse

PROMPTS_DIR = Path(__file__).parent / "prompts"

MAX_RETRIES = 5
MAX_AGENT_TURNS = 20


@lru_cache
def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text()


def _get_client() -> anthropic.AsyncAnthropic:
    settings = get_settings()
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


CREATE_BLOCK_TOOL = {
    "name": "create_block",
    "description": "Create a block from the writing with its questions. Call this once per block.",
    "input_schema": CreateBlockInput.model_json_schema(),
}

QUESTIONS_TOOL = {
    "name": "return_questions",
    "description": "Return the generated questions.",
    "input_schema": QuestionsResponse.model_json_schema(),
}

EVALUATION_TOOL = {
    "name": "return_evaluation",
    "description": "Return the evaluation score and feedback.",
    "input_schema": EvaluationResponse.model_json_schema(),
}


async def _call_with_retry(coro_fn, *args, **kwargs):  # type: ignore[no-untyped-def]
    """Call an async function with exponential backoff on rate limit errors."""
    for attempt in range(MAX_RETRIES):
        try:
            return await coro_fn(*args, **kwargs)
        except anthropic.RateLimitError:
            if attempt == MAX_RETRIES - 1:
                raise
            wait = (2**attempt) + random.uniform(0, 1)
            await asyncio.sleep(wait)


async def create_blocks(text: str, num_questions: int) -> list[CreateBlockInput]:
    """Agentic loop: LLM reads full text, creates blocks with questions via tool calls."""
    client = _get_client()
    settings = get_settings()

    messages: list[dict] = [
        {
            "role": "user",
            "content": _load_prompt("create_blocks_user").format(
                num_questions=num_questions, text=text
            ),
        },
    ]

    blocks: list[CreateBlockInput] = []

    for _ in range(MAX_AGENT_TURNS):
        resp = await _call_with_retry(
            client.messages.create,
            model=settings.llm_model,
            max_tokens=4096,
            system=_load_prompt("create_blocks_system"),
            messages=messages,
            tools=[CREATE_BLOCK_TOOL],
        )

        # Collect tool calls from this turn
        tool_uses = [b for b in resp.content if b.type == "tool_use"]

        if not tool_uses:
            # Model is done — no more tool calls
            break

        for tool_use in tool_uses:
            if tool_use.name == "create_block":
                block = CreateBlockInput.model_validate(tool_use.input)
                blocks.append(block)

        # Send tool results back so the model can continue
        messages.append({"role": "assistant", "content": resp.content})
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": "Block created.",
                    }
                    for tool_use in tool_uses
                ],
            }
        )

        if resp.stop_reason == "end_turn":
            break

    return blocks


async def generate_questions(
    content: str,
    num_questions: int,
    existing_questions: list[str] | None = None,
) -> list[str]:
    """Generate additional questions for an existing block."""
    client = _get_client()
    settings = get_settings()

    if existing_questions:
        numbered = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(existing_questions))
        existing_section = (
            f"The following questions have already been asked. "
            f"Do NOT repeat or rephrase any of them:\n{numbered}"
        )
    else:
        existing_section = ""

    resp = await _call_with_retry(
        client.messages.create,
        model=settings.llm_model,
        max_tokens=1024,
        system=_load_prompt("generate_questions_system"),
        messages=[
            {
                "role": "user",
                "content": _load_prompt("generate_questions_user").format(
                    num_questions=num_questions,
                    content=content,
                    existing_questions_section=existing_section,
                ),
            },
        ],
        tools=[QUESTIONS_TOOL],
        tool_choice={"type": "tool", "name": "return_questions"},
    )

    for block in resp.content:
        if block.type == "tool_use" and block.name == "return_questions":
            data = QuestionsResponse.model_validate(block.input)
            return data.questions[:num_questions]

    return []


async def evaluate_answer(
    question: str, answer: str, context: str
) -> EvaluationResponse:
    """Evaluate an answer and return score + feedback."""
    client = _get_client()
    settings = get_settings()

    resp = await _call_with_retry(
        client.messages.create,
        model=settings.llm_model,
        max_tokens=1024,
        system=_load_prompt("evaluate_answer_system"),
        messages=[
            {
                "role": "user",
                "content": _load_prompt("evaluate_answer_user").format(
                    context=context, question=question, answer=answer
                ),
            },
        ],
        tools=[EVALUATION_TOOL],
        tool_choice={"type": "tool", "name": "return_evaluation"},
    )

    for block in resp.content:
        if block.type == "tool_use" and block.name == "return_evaluation":
            return EvaluationResponse.model_validate(block.input)

    return EvaluationResponse(score=0, feedback="")
