"use client"

import { useState } from "react"
import { Pencil, Trash2, Check, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useDeleteSmallWin, useUpdateSmallWin } from "@/hooks/useSmallWins"
import type { SmallWinResponse } from "@/types/small-win"

interface SmallWinListProps {
  wins: SmallWinResponse[]
  date: string
}

interface WinItemProps {
  win: SmallWinResponse
  date: string
}

function WinItem({ win, date }: WinItemProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(win.text)
  const update = useUpdateSmallWin()
  const remove = useDeleteSmallWin()

  async function handleSave() {
    if (!draft.trim() || draft === win.text) {
      setEditing(false)
      setDraft(win.text)
      return
    }
    await update.mutateAsync({ id: win.id, date, body: { text: draft.trim() } })
    setEditing(false)
  }

  function handleCancel() {
    setDraft(win.text)
    setEditing(false)
  }

  return (
    <div className="flex gap-3 items-start p-4 rounded-lg border bg-card">
      <div className="flex-1 min-w-0">
        {editing ? (
          <Textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            maxLength={500}
            rows={2}
            autoFocus
            disabled={update.isPending}
          />
        ) : (
          <p className="text-sm leading-relaxed break-words">{win.text}</p>
        )}
      </div>
      <div className="flex gap-1 shrink-0">
        {editing ? (
          <>
            <Button
              size="icon"
              variant="ghost"
              onClick={handleSave}
              disabled={update.isPending}
              aria-label="Save"
            >
              <Check className="h-4 w-4 text-green-600" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={handleCancel}
              aria-label="Cancel"
            >
              <X className="h-4 w-4" />
            </Button>
          </>
        ) : (
          <>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => setEditing(true)}
              aria-label="Edit"
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => remove.mutate({ id: win.id, date })}
              disabled={remove.isPending}
              aria-label="Delete"
            >
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </>
        )}
      </div>
    </div>
  )
}

export function SmallWinList({ wins, date }: SmallWinListProps) {
  if (wins.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-8">
        No wins logged for this day yet.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {wins.map((win) => (
        <WinItem key={win.id} win={win} date={date} />
      ))}
    </div>
  )
}
