"use client"

import { useState } from "react"
import { QuestionBlock, BlockTree, submitAnswer, evaluateAnswer } from "../lib/api"
import { Button } from "@workspace/ui/components/button"
import { Badge } from "@workspace/ui/components/badge"
import AnswerForm from "./answer-form"

type QuestionBlockViewProps = {
    question: QuestionBlock
    treeId: string
    depth: number
    onTreeUpdate: (tree: BlockTree) => void
}

export default function QuestionBlockView({ question, treeId, depth, onTreeUpdate }: QuestionBlockViewProps) {
    const [showAnswerForm, setShowAnswerForm] = useState(false)

    async function handleSubmitAnswer(content: string) {
        const updatedTree = await submitAnswer(treeId, question.id, content)
        onTreeUpdate(updatedTree)
        setShowAnswerForm(false)
    }

    async function handleEvaluate() {
        if (!question.answer) return
        const updatedTree = await evaluateAnswer(treeId, question.answer.id)
        onTreeUpdate(updatedTree)
    }

    return (
        <div className={`border-l-2 border-muted pl-4 py-2 ${depth > 0 ? "ml-4" : ""}`}>
            <p className="font-medium text-sm">❓ {question.content}</p>

            {question.answer ? (
                <div className="mt-2 space-y-2">
                    <div className="bg-muted/50 rounded-lg p-3">
                        <p className="text-sm">{question.answer.content}</p>
                    </div>

                    {question.answer.score !== null && (
                        <div className="flex items-center gap-2">
                            <Badge variant={question.answer.score >= 70 ? "default" : "destructive"}>
                                {question.answer.score}/100
                            </Badge>
                            {question.answer.feedback && (
                                <span className="text-xs text-muted-foreground">{question.answer.feedback}</span>
                            )}
                        </div>
                    )}

                    <div className="flex gap-2">
                        {question.answer.score === null && (
                            <Button variant="outline" size="sm" onClick={handleEvaluate}>
                                Evaluate
                            </Button>
                        )}
                        <Button variant="ghost" size="sm" onClick={() => setShowAnswerForm(true)}>
                            Rewrite
                        </Button>
                    </div>

                    {showAnswerForm && (
                        <AnswerForm
                            onSubmit={handleSubmitAnswer}
                            onCancel={() => setShowAnswerForm(false)}
                            initialValue={question.answer.content}
                        />
                    )}

                    {question.answer.questions.map(childQuestion => (
                        <QuestionBlockView
                            key={childQuestion.id}
                            question={childQuestion}
                            treeId={treeId}
                            depth={depth + 1}
                            onTreeUpdate={onTreeUpdate}
                        />
                    ))}
                </div>
            ) : (
                <div className="mt-2">
                    {showAnswerForm ? (
                        <AnswerForm
                            onSubmit={handleSubmitAnswer}
                            onCancel={() => setShowAnswerForm(false)}
                        />
                    ) : (
                        <Button variant="outline" size="sm" onClick={() => setShowAnswerForm(true)}>
                            Answer
                        </Button>
                    )}
                </div>
            )}
        </div>
    )
}
