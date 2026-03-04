"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useCreateSmallWin } from "@/hooks/useSmallWins"
import { getToday, cn } from "@/lib/utils"
import type { SmallWinCategory } from "@/types/small-win"

interface SmallWinFormProps {
  date: string
}

type Mode = "win" | "task"

const CATEGORIES: SmallWinCategory[] = ["Work", "Health", "Personal Growth", "General"]

export function SmallWinForm({ date }: SmallWinFormProps) {
  const isFuture = date > getToday()
  const [mode, setMode] = useState<Mode>(isFuture ? "task" : "win")
  const [text, setText] = useState("")
  const [category, setCategory] = useState<SmallWinCategory | null>(null)
  const create = useCreateSmallWin()

  // Reset mode when navigating between dates
  useEffect(() => {
    setMode(isFuture ? "task" : "win")
    setText("")
    setCategory(null)
  }, [date, isFuture])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!text.trim()) return
    try {
      await create.mutateAsync({
        date,
        text: text.trim(),
        entry_type: mode,
        category: category ?? null,
      })
      setText("")
      setCategory(null)
    } catch (err) {
      toast.error("Failed to log win")
      console.error("[SmallWinForm] submit failed:", err)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {!isFuture && (
        <div className="flex rounded-md border overflow-hidden">
          <button
            type="button"
            onClick={() => setMode("win")}
            className={`flex-1 py-1.5 text-sm font-medium transition-colors ${
              mode === "win"
                ? "bg-primary text-primary-foreground"
                : "bg-background text-muted-foreground hover:bg-muted"
            }`}
          >
            Log Win
          </button>
          <button
            type="button"
            onClick={() => setMode("task")}
            className={`flex-1 py-1.5 text-sm font-medium transition-colors ${
              mode === "task"
                ? "bg-primary text-primary-foreground"
                : "bg-background text-muted-foreground hover:bg-muted"
            }`}
          >
            Log Task
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        {mode === "win" ? (
          <Textarea
            placeholder="What did you accomplish today?"
            value={text}
            onChange={(e) => setText(e.target.value)}
            maxLength={500}
            rows={3}
            disabled={create.isPending}
          />
        ) : (
          <Input
            placeholder="What do you need to do?"
            value={text}
            onChange={(e) => setText(e.target.value)}
            maxLength={500}
            disabled={create.isPending}
          />
        )}

        {/* Category pills */}
        <div className="flex flex-wrap gap-1.5">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setCategory((prev) => (prev === cat ? null : cat))}
              className={cn(
                "px-2.5 py-1 rounded-full text-xs font-medium border transition-colors",
                category === cat
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-background text-muted-foreground border-border hover:border-foreground"
              )}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">{text.length}/500</span>
          <Button type="submit" disabled={!text.trim() || create.isPending}>
            {create.isPending ? "Saving…" : mode === "win" ? "Log Win" : "Add Task"}
          </Button>
        </div>

        {create.isError && (
          <p className="text-sm text-destructive">{create.error.message}</p>
        )}
      </form>
    </div>
  )
}
