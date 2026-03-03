"use client"

import { Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useDeleteFoodLog } from "@/hooks/useFoodLogs"
import type { FoodLogResponse } from "@/types/food-log"

interface FoodLogListProps {
  entries: FoodLogResponse[]
  date: string
}

interface FoodLogItemProps {
  entry: FoodLogResponse
  date: string
}

function FoodLogItem({ entry, date }: FoodLogItemProps) {
  const remove = useDeleteFoodLog()

  return (
    <div className="flex flex-col gap-1 p-3 rounded-lg border bg-card">
      <div className="flex items-start gap-3">
        <span className="text-xs text-muted-foreground font-mono shrink-0 mt-0.5">
          {entry.consumed_at}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium">{entry.food_item}</p>
          {entry.ai_comment && (
            <p className="text-xs text-muted-foreground mt-1 italic">
              {entry.ai_comment}
            </p>
          )}
        </div>
        <Button
          size="icon"
          variant="ghost"
          className="h-7 w-7 shrink-0"
          onClick={() => remove.mutate({ id: entry.id, date })}
          disabled={remove.isPending}
          aria-label="Delete"
        >
          <Trash2 className="h-3.5 w-3.5 text-destructive" />
        </Button>
      </div>
    </div>
  )
}

export function FoodLogList({ entries, date }: FoodLogListProps) {
  if (entries.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-6">
        No meals logged for this day.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {entries.map((entry) => (
        <FoodLogItem key={entry.id} entry={entry} date={date} />
      ))}
    </div>
  )
}
