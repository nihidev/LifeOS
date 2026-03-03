"use client"

import { useState } from "react"
import { Pencil, Trash2, Check, X, Trophy, Square } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useDeleteSmallWin, useToggleComplete, useUpdateSmallWin } from "@/hooks/useSmallWins"
import type { SmallWinResponse } from "@/types/small-win"
import { cn } from "@/lib/utils"

interface SmallWinListProps {
  wins: SmallWinResponse[]
  date: string
}

interface WinItemProps {
  win: SmallWinResponse
  date: string
}

function EntryIcon({ win, date }: { win: SmallWinResponse; date: string }) {
  const toggle = useToggleComplete()
  const isTask = win.entry_type === "task"
  const isCompleted = win.completed === true

  if (!isTask) {
    return <Trophy className="h-4 w-4 shrink-0 mt-0.5 text-amber-500" />
  }

  // Incomplete task → Circle; completed task → Trophy (both clickable to toggle)
  return (
    <button
      type="button"
      onClick={() => toggle.mutate({ id: win.id, date, completed: !isCompleted })}
      disabled={toggle.isPending}
      className="shrink-0 mt-0.5 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      aria-label={isCompleted ? "Mark incomplete" : "Mark complete"}
    >
      {isCompleted ? (
        <Trophy className="h-4 w-4 text-amber-500" />
      ) : (
        <Square className="h-4 w-4 text-muted-foreground" />
      )}
    </button>
  )
}

function WinItem({ win, date }: WinItemProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(win.text)
  const update = useUpdateSmallWin()
  const remove = useDeleteSmallWin()

  const isTask = win.entry_type === "task"
  const isCompleted = win.completed === true

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
      <EntryIcon win={win} date={date} />

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
          <p
            className={cn(
              "text-sm leading-relaxed break-words",
              isTask && isCompleted && "line-through text-muted-foreground"
            )}
          >
            {win.text}
          </p>
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
        No wins or tasks logged for this day yet.
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
