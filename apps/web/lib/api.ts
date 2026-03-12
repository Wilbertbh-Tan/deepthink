const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"


export type AnswerBlock = {
    id: string
    content: string
    score: number | null
    feedback: string | null
    questions: QuestionBlock[]
}

export type QuestionBlock = {
    id: string
    content: string
    answer: AnswerBlock | null
}

export type TitleBlock = {
    id: string
    content: string
    questions: QuestionBlock[]
}

export type BlockTree = {
    id: string
    title: string
    original_text: string
    blocks: TitleBlock[]
    num_questions: number
}

export type TreeListItem = {
    id: string
    title: string
    num_blocks: number
    num_questions: number
}


export async function listTrees(): Promise<TreeListItem[]> {
    const response = await fetch(`${API_BASE}/trees`)
    return response.json()
}

export async function getTree(id: string): Promise<BlockTree> {
    const response = await fetch(`${API_BASE}/trees/${id}`)
    return response.json()
}

export async function createTree(title: string, content: string, num_questions: number): Promise<BlockTree> {
    const response = await fetch(`${API_BASE}/trees`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content, num_questions }),
    })
    return response.json()
}

export async function deleteTree(id: string): Promise<void> {
    await fetch(`${API_BASE}/trees/${id}`, { method: "DELETE" })
}

export async function submitAnswer(treeId: string, questionId: string, content: string): Promise<BlockTree> {
    const response = await fetch(`${API_BASE}/trees/${treeId}/questions/${questionId}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
    })
    return response.json()
}

export async function evaluateAnswer(treeId: string, answerId: string): Promise<BlockTree> {
    const response = await fetch(`${API_BASE}/trees/${treeId}/answers/${answerId}/evaluate`, {
        method: "POST",
    })
    return response.json()
}

export async function generateQuestions(treeId: string, blockId: string): Promise<BlockTree> {
    const response = await fetch(`${API_BASE}/trees/${treeId}/blocks/${blockId}/questions`, {
        method: "POST",
    })
    return response.json()
}
