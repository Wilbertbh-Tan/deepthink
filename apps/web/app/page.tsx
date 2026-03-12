"use client"

import { useEffect, useState } from "react"
import { listTrees, deleteTree, TreeListItem } from "../lib/api"
import Link from "next/link"
import { Button } from "@workspace/ui/components/button"
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from "@workspace/ui/components/card"

export default function Dashboard() {
    const [trees, setTrees] = useState<TreeListItem[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        listTrees().then(data => {
            setTrees(data)
            setLoading(false)
        })
    }, [])

    async function handleDelete(id: string) {
        await deleteTree(id)
        setTrees(trees.filter(t => t.id !== id))
    }

    if (loading) return <p className="text-muted-foreground">Loading...</p>

    return (
        <div>
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-3xl font-bold">My Trees</h1>
                <Link href="/new">
                    <Button>+ New Tree</Button>
                </Link>
            </div>

            {trees.length === 0 && (
                <p className="text-muted-foreground text-center py-12">No trees yet. Create one to get started.</p>
            )}

            <div className="grid gap-4">
                {trees.map(tree => (
                    <Card key={tree.id}>
                        <CardHeader>
                            <Link href={`/trees/${tree.id}`} className="hover:underline">
                                <CardTitle>{tree.title}</CardTitle>
                            </Link>
                            <CardDescription>
                                {tree.num_blocks} blocks · {tree.num_questions} questions
                            </CardDescription>
                        </CardHeader>
                        <CardFooter>
                            <Button variant="destructive" size="sm" onClick={() => handleDelete(tree.id)}>
                                Delete
                            </Button>
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    )
}
