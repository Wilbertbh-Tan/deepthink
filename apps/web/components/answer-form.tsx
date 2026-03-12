"use client"

import { useState } from "react"
import { Button } from "@workspace/ui/components/button"
import { Textarea } from "@workspace/ui/components/textarea"

type AnswerFormProps = {
    onSubmit: (content: string) => Promise<void>
    onCancel?: () => void
    initialValue?: string
}

export default function AnswerForm({ onSubmit, onCancel, initialValue = "" }: AnswerFormProps) {
    const [content, setContent] = useState(initialValue)
    const [loading, setLoading] = useState(false)

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        if (!content.trim()) return
        setLoading(true)
        await onSubmit(content)
        setContent("")
        setLoading(false)
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-3 mt-2">
            <Textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={4}
                placeholder="Write your answer..."
            />
            <div className="flex gap-2">
                <Button type="submit" size="sm" disabled={loading}>
                    {loading ? "Submitting..." : "Submit"}
                </Button>
                {onCancel && (
                    <Button type="button" variant="outline" size="sm" onClick={onCancel}>
                        Cancel
                    </Button>
                )}
            </div>
        </form>
    )
}
