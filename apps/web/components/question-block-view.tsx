"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  MessageSquare,
  PenLine,
  Plus,
  Star,
  Loader2,
} from "lucide-react";
import { Button } from "@workspace/ui/components/button";
import { Badge } from "@workspace/ui/components/badge";
import { Separator } from "@workspace/ui/components/separator";
import type { QuestionBlock, BlockTree } from "@/lib/api";
import {
  submitAnswer,
  generateQuestions,
} from "@/lib/api";
import { AnswerForm } from "./answer-form";

interface QuestionBlockViewProps {
  question: QuestionBlock;
  treeId: string;
  onTreeUpdate: (tree: BlockTree) => void;
  depth?: number;
}

export function QuestionBlockView({
  question,
  treeId,
  onTreeUpdate,
  depth = 0,
}: QuestionBlockViewProps) {
  const [generating, setGenerating] = useState(false);
  const [rewriting, setRewriting] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmitAnswer(content: string) {
    setSubmitting(true);
    try {
      const updated = await submitAnswer(treeId, question.id, content);
      onTreeUpdate(updated);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleGenerateMore() {
    if (!question.answer) return;
    setGenerating(true);
    try {
      const updated = await generateQuestions(treeId, question.answer.id, 1);
      onTreeUpdate(updated);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div
      className={`border-l-2 pl-4 ${depth > 0 ? "border-muted ml-2" : "border-primary/30"}`}
    >
      <div className="flex items-start gap-2 py-2">
        <MessageSquare className="text-primary mt-0.5 h-4 w-4 shrink-0" />
        <p className="text-sm font-medium">{question.content}</p>
      </div>

      {submitting ? (
        <div className="ml-6 flex items-center gap-2 py-4 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Evaluating your answer...
        </div>
      ) : question.answer ? (
        <div className="ml-6">
          <div className="bg-muted/50 rounded-md p-3">
            <p className="text-sm whitespace-pre-wrap">
              {question.answer.content}
            </p>

            {question.answer.score !== null && (
              <div className="mt-2 flex items-center gap-2">
                <Badge
                  variant={
                    question.answer.score >= 70 ? "default" : "secondary"
                  }
                  className="text-xs"
                >
                  <Star className="mr-1 h-3 w-3" />
                  {question.answer.score}/100
                </Badge>
              </div>
            )}

            {question.answer.feedback && (
              <div className="text-muted-foreground mt-2 text-sm [&_p]:mb-1 [&_ul]:list-disc [&_ul]:pl-4 [&_ol]:list-decimal [&_ol]:pl-4 [&_li]:mb-0.5 [&_strong]:text-foreground [&_h1]:text-base [&_h2]:text-sm [&_h3]:text-sm [&_h1]:font-semibold [&_h2]:font-semibold [&_h3]:font-semibold [&_code]:bg-muted [&_code]:px-1 [&_code]:rounded">
                <ReactMarkdown>{question.answer.feedback}</ReactMarkdown>
              </div>
            )}
          </div>

          <div className="mt-2 flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleGenerateMore}
              disabled={generating}
            >
              {generating ? (
                <Loader2 className="mr-1 h-3 w-3 animate-spin" />
              ) : (
                <Plus className="mr-1 h-3 w-3" />
              )}
              More Questions
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setRewriting(true)}
            >
              <PenLine className="mr-1 h-3 w-3" />
              Rewrite
            </Button>
          </div>

          {rewriting && (
            <div className="mt-2">
              <AnswerForm
                onSubmit={async (content) => {
                  await handleSubmitAnswer(content);
                  setRewriting(false);
                }}
                onCancel={() => setRewriting(false)}
                initialValue={question.answer.content}
              />
            </div>
          )}

          {question.answer.children_questions.length > 0 && (
            <div className="mt-3">
              <Separator className="mb-3" />
              {question.answer.children_questions.map((childQ) => (
                <QuestionBlockView
                  key={childQ.id}
                  question={childQ}
                  treeId={treeId}
                  onTreeUpdate={onTreeUpdate}
                  depth={depth + 1}
                />
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="ml-6">
          <AnswerForm onSubmit={handleSubmitAnswer} />
        </div>
      )}
    </div>
  );
}
