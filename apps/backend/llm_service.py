import json
from pathlib import Path

from openai import OpenAI

from .config import get_settings
from .models import CreateBlockInput, EvaluationResponse, QuestionsResponse

_PROMPTS = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPTS / name).read_text()


def _get_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )


def create_blocks(text: str, num_questions: int = 2) -> list[CreateBlockInput]:
    client = _get_client()
    settings = get_settings()

    system = _load_prompt("create_blocks_system.md")
    user = _load_prompt("create_blocks_user.md").format(
        text=text, num_questions=num_questions
    )

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "create_block",
                    "description": "Create a block from the text with questions",
                    "parameters": CreateBlockInput.model_json_schema(),
                },
            }
        ],
    )

    # Extract all tool calls from the response
    blocks = []
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            if not hasattr(tool_call, "function"):
                continue
            data = json.loads(tool_call.function.arguments)
            blocks.append(CreateBlockInput(**data))

    return blocks


def generate_questions(
    content: str, num_questions: int = 2, existing_questions: list[str] | None = None
) -> list[str]:
    client = _get_client()
    settings = get_settings()

    system = _load_prompt("generate_questions_system.md")
    user = _load_prompt("generate_questions_user.md").format(
        content=content,
        num_questions=num_questions,
        existing_questions_section=existing_questions,
    )

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "generate_questions",
                    "description": "Generate follow-up questions",
                    "parameters": QuestionsResponse.model_json_schema(),
                },
            }
        ],
    )

    # Extract all tool calls from the response
    blocks = []
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            if not hasattr(tool_call, "function"):
                continue
            data = json.loads(tool_call.function.arguments)
            blocks.extend(data["questions"])

    return blocks


def evaluate_answer(question: str, answer: str, context: str) -> EvaluationResponse:
    client = _get_client()
    settings = get_settings()

    system = _load_prompt("evaluate_answer_system.md")
    user = _load_prompt("evaluate_answer_user.md").format(
        question=question, answer=answer, context=context
    )

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "evaluate_answer",
                    "description": "Scores an answer 0-100",
                    "parameters": EvaluationResponse.model_json_schema(),
                },
            }
        ],
    )

    # Extract all tool calls from the response
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            if not hasattr(tool_call, "function"):
                continue
            data = json.loads(tool_call.function.arguments)
            data = EvaluationResponse(**data)
    return data
