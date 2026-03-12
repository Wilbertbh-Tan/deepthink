"use client"

import { TitleBlock, BlockTree, generateQuestions } from "../lib/api"
import { Button } from "@workspace/ui/components/button"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@workspace/ui/components/card"
import QuestionBlockView from "./question-block-view"

type TitleBlockViewProps = {
    block: TitleBlock
    treeId: string
    index: number
    onTreeUpdate: (tree: BlockTree) => void
}

export default function TitleBlockView({ block, treeId, index, onTreeUpdate }: TitleBlockViewProps) {

    async function handleAddQuestions() {
        const updatedTree = await generateQuestions(treeId, block.id)
        onTreeUpdate(updatedTree)
    }

    return (
        <Card className="mb-6">
            <CardHeader>
                <CardTitle className="text-lg">Block {index + 1}</CardTitle>
            </CardHeader>
            <CardContent>
                <p className="text-sm text-muted-foreground mb-4">{block.content}</p>

                <div className="space-y-3">
                    {block.questions.map(question => (
                        <QuestionBlockView
                            key={question.id}
                            question={question}
                            treeId={treeId}
                            depth={0}
                            onTreeUpdate={onTreeUpdate}
                        />
                    ))}
                </div>
            </CardContent>
            <CardFooter>
                <Button variant="outline" size="sm" onClick={handleAddQuestions}>
                    + Add Questions
                </Button>
            </CardFooter>
        </Card>
    )
}
