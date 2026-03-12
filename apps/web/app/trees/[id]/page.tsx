"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { getTree, BlockTree } from "../../../lib/api"
import { Badge } from "@workspace/ui/components/badge"
import TitleBlockView from "../../../components/title-block-view"
import Link from "next/link"

export default function TreeDetail() {
    const { id } = useParams()
    const [tree, setTree] = useState<BlockTree | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (typeof id === "string") {
            getTree(id).then(data => {
                setTree(data)
                setLoading(false)
            })
        }
    }, [id])

    if (loading) return <p className="text-muted-foreground">Loading...</p>
    if (!tree) return <p className="text-red-500">Tree not found</p>

    return (
        <div>
            <Link href="/" className="text-muted-foreground hover:underline text-sm">
                ← Back
            </Link>
            <div className="flex items-center gap-3 mt-4 mb-8">
                <h1 className="text-3xl font-bold">{tree.title}</h1>
                <Badge variant="outline">{tree.blocks.length} blocks</Badge>
            </div>

            {tree.blocks.map((block, index) => (
                <TitleBlockView
                    key={block.id}
                    block={block}
                    treeId={tree.id}
                    index={index}
                    onTreeUpdate={setTree}
                />
            ))}
        </div>
    )
}
