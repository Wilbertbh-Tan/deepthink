"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { createTree } from "../../lib/api"
import { Button } from "@workspace/ui/components/button"
import { Input } from "@workspace/ui/components/input"
import { Textarea } from "@workspace/ui/components/textarea"
import Link from "next/link"

export default function NewTree() {
    const router = useRouter()
    const [title, setTitle] = useState("")
    const [content, setContent] = useState("")
    const [numQuestions, setNumQuestions] = useState(3)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        setLoading(true)
        setError("")

        try {
            const tree = await createTree(title, content, numQuestions)
            router.push(`/trees/${tree.id}`)
        } catch (err) {
            setError("Failed to create tree")
            setLoading(false)
        }
    }

    return (
        <div>
            <Link href="/" className="text-muted-foreground hover:underline text-sm">
                ← Back
            </Link>
            <h1 className="text-3xl font-bold mt-4 mb-8">New Tree</h1>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                    <label className="text-sm font-medium">Title</label>
                    <Input
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Give your writing a title"
                        required
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium">Content</label>
                    <Textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        rows={10}
                        placeholder="Paste or write your text here..."
                        required
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium">Questions per block</label>
                    <Input
                        type="number"
                        value={numQuestions}
                        onChange={(e) => setNumQuestions(Number(e.target.value))}
                        min={1}
                        max={10}
                        className="w-24"
                    />
                </div>
                {error && <p className="text-red-500 text-sm">{error}</p>}
                <Button type="submit" disabled={loading}>
                    {loading ? "Creating..." : "Create Tree"}
                </Button>
            </form>
        </div>
    )
}
