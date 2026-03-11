"use client";

import { useState } from "react";
import { Send, X } from "lucide-react";
import { Button } from "@workspace/ui/components/button";
import { Textarea } from "@workspace/ui/components/textarea";

interface AnswerFormProps {
  onSubmit: (content: string) => Promise<void>;
  onCancel?: () => void;
  initialValue?: string;
}

export function AnswerForm({ onSubmit, onCancel, initialValue = "" }: AnswerFormProps) {
  const [content, setContent] = useState(initialValue);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;
    setLoading(true);
    try {
      await onSubmit(content);
      setContent("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-2 flex flex-col gap-2">
      <Textarea
        placeholder="Write your answer..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={3}
        className="text-sm"
      />
      <div className="flex gap-2">
        <Button
          type="submit"
          size="sm"
          disabled={loading || !content.trim()}
        >
          <Send className="mr-1 h-3 w-3" />
          {loading ? "Submitting..." : "Submit Answer"}
        </Button>
        {onCancel && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onCancel}
            disabled={loading}
          >
            <X className="mr-1 h-3 w-3" />
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
