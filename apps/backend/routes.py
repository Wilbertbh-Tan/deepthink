import uuid

from fastapi import APIRouter, HTTPException

from . import storage
from . import llm_service
from .models import (
    BlockTree,
    CreateTreeRequest,
    GenerateQuestionsRequest,
    QuestionBlock,
    SubmitAnswerRequest,
    TitleBlock,
    TreeListItem,
    AnswerBlock,
)

router = APIRouter(prefix="/api")


# --- Tree CRUD ---


@router.post("/trees")
async def create_tree(request: CreateTreeRequest) -> BlockTree:
    tree = BlockTree(
        id=str(uuid.uuid4()),
        title=request.title,
        original_text=request.text,
        num_questions=request.num_questions,
    )
    raw_blocks = llm_service.create_blocks(request.text, request.num_questions)
    for raw in raw_blocks:
        block = TitleBlock(
            id=str(uuid.uuid4()),
            content=raw.content,
            questions=[
                QuestionBlock(id=str(uuid.uuid4()), content=q) for q in raw.questions
            ],
        )
        tree.blocks.append(block)
    storage.save_tree(tree.id, tree.model_dump())
    return tree


@router.get("/trees")
async def list_trees() -> list[TreeListItem]:
    trees = storage.list_trees()
    result = []
    for t in trees:
        tree = BlockTree(**t)
        total_questions = sum(len(b.questions) for b in tree.blocks)
        result.append(
            TreeListItem(
                id=tree.id,
                title=tree.title,
                num_blocks=len(tree.blocks),
                num_questions=total_questions,
            )
        )
    return result


@router.get("/trees/{tree_id}")
async def get_tree(tree_id: str) -> BlockTree:
    data = storage.load_tree(tree_id)
    if not data:
        raise HTTPException(status_code=404, detail="Tree not found")
    return BlockTree(**data)


@router.delete("/trees/{tree_id}")
async def delete_tree(tree_id: str):
    if not storage.delete_tree(tree_id):
        raise HTTPException(status_code=404, detail="Tree not found")
    return {"ok": True}


# --- Questions & Answers ---
@router.post("/trees/{tree_id}/questions/{question_id}/answer")
async def submit_answer(tree_id: str, question_id: str, request: SubmitAnswerRequest):
    # Step 1: Load the tree
    data = storage.load_tree(tree_id)
    if not data:
        raise HTTPException(status_code=404, detail="Tree not found")
    tree = BlockTree(**data)

    # Step 2: Find the question
    found = None
    for block in tree.blocks:
        for question in block.questions:
            if question.id == question_id:
                found = question
                break
    if not found:
        raise HTTPException(status_code=404, detail="Question not found")

    answer = AnswerBlock(id=str(uuid.uuid4()), content=request.content)
    found.answer = answer

    # Step 4: Save and return
    storage.save_tree(tree.id, tree.model_dump())
    return tree

    # --- Generate Questions ---


@router.post("/trees/{tree_id}/blocks/{block_id}/questions")
async def add_questions(tree_id: str, block_id: str, request: GenerateQuestionsRequest):
    data = storage.load_tree(tree_id)
    if not data:
        raise HTTPException(status_code=404, detail="Tree not found")
    tree = BlockTree(**data)

    found_block = None
    for block in tree.blocks:
        if block.id == block_id:
            found_block = block
            break
    if not found_block:
        raise HTTPException(status_code=404, detail="Block not found")

    existing = [q.content for q in found_block.questions]
    new_questions = llm_service.generate_questions(
        found_block.content, request.num_questions, existing
    )

    for q in new_questions:
        found_block.questions.append(QuestionBlock(id=str(uuid.uuid4()), content=q))

    storage.save_tree(tree.id, tree.model_dump())
    return tree

    # --- Evaluation ---


@router.post("/trees/{tree_id}/answers/{answer_id}/evaluate")
async def evaluate_answer(tree_id: str, answer_id: str):
    data = storage.load_tree(tree_id)
    if not data:
        raise HTTPException(status_code=404, detail="Tree not found")
    tree = BlockTree(**data)

    found_answer = None
    found_question = None
    for block in tree.blocks:
        for question in block.questions:
            if question.answer and question.answer.id == answer_id:
                found_answer = question.answer
                found_question = question
                found_block = block
                break

    if not found_answer or not found_question:
        raise HTTPException(status_code=404, detail="Answer not found")

    result = llm_service.evaluate_answer(
        found_question.content, found_answer.content, found_block.content
    )
    found_answer.score = result.score
    found_answer.feedback = result.feedback

    storage.save_tree(tree.id, tree.model_dump())
    return tree
