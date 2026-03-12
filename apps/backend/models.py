from __future__ import annotations

from pydantic import BaseModel, Field


# --- Core tree models ---


class AnswerBlock(BaseModel):
    id: str
    content: str
    score: int | None = None
    feedback: str | None = None
    children_questions: list[QuestionBlock] = Field(default_factory=list)


class QuestionBlock(BaseModel):
    id: str
    content: str
    answer: AnswerBlock | None = None


class TitleBlock(BaseModel):
    id: str
    content: str
    questions: list[QuestionBlock] = Field(default_factory=list)


class BlockTree(BaseModel):
    id: str
    title: str
    original_text: str
    blocks: list[TitleBlock] = Field(default_factory=list)
    num_questions: int = 2


# --- LLM structured output models ---
# TODO(human): Add the models that define what the LLM returns.
# You need three models:
# 1. CreateBlockInput - what the LLM returns when splitting text (content + questions)
# 2. QuestionsResponse - what the LLM returns when generating questions
# 3. EvaluationResponse - what the LLM returns when scoring an answer (score + feedback)


class CreateBlockInput(BaseModel):
    content: str
    questions: list[str]


class QuestionsResponse(BaseModel):
    questions: list[str]


class EvaluationResponse(BaseModel):
    score: int
    feedback: str


# --- Request / Response models ---
class CreateTreeRequest(BaseModel):
    title: str
    text: str
    num_questions: int = 2


class SubmitAnswerRequest(BaseModel):
    content: str


class GenerateQuestionsRequest(BaseModel):
    num_questions: int = 2


class TreeListItem(BaseModel):
    id: str
    title: str
    num_blocks: int
    num_questions: int
