"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useCreateSmallWin } from "@/hooks/useSmallWins"

interface SmallWinFormProps {
  date: string
}

export function SmallWinForm({ date }: SmallWinFormProps) {
  const [text, setText] = useState("")
  const create = useCreateSmallWin()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!text.trim()) return
    try {
      await create.mutateAsync({ date, text: text.trim() })
      setText("")
    } catch (err) {
      console.error("[SmallWinForm] submit failed:", err)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <Textarea
        placeholder="What did you accomplish today?"
        value={text}
        onChange={(e) => setText(e.target.value)}
        maxLength={500}
        rows={3}
        disabled={create.isPending}
      />
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">{text.length}/500</span>
        <Button type="submit" disabled={!text.trim() || create.isPending}>
          {create.isPending ? "Saving…" : "Log Win"}
        </Button>
      </div>
      {create.isError && (
        <p className="text-sm text-destructive">{create.error.message}</p>
      )}
    </form>
  )
}
