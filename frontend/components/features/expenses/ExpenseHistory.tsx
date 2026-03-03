"use client"

import { useState } from "react"
import { ChevronDown, ChevronUp } from "lucide-react"
import { useAllExpenses } from "@/hooks/useExpenses"
import type { ExpenseResponse } from "@/types/expense"

function formatHistoryDate(dateStr: string): string {
  const [y, m, d] = dateStr.split("-").map(Number)
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  })
}

interface DateGroup {
  date: string
  entries: ExpenseResponse[]
  total: number
}

function groupByDate(expenses: ExpenseResponse[]): DateGroup[] {
  const map = new Map<string, ExpenseResponse[]>()
  for (const e of expenses) {
    const list = map.get(e.date) ?? []
    list.push(e)
    map.set(e.date, list)
  }
  return Array.from(map.entries())
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([date, entries]) => ({
      date,
      entries,
      total: entries.reduce((sum, e) => sum + Number(e.amount), 0),
    }))
}

function DateGroupRow({ group }: { group: DateGroup }) {
  const [open, setOpen] = useState(true)

  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-3 bg-muted/40 hover:bg-muted/70 transition-colors"
      >
        <div className="flex items-center gap-2">
          {open ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
          <span className="text-sm font-medium">{formatHistoryDate(group.date)}</span>
          <span className="text-xs bg-primary/10 text-primary font-semibold rounded-full px-1.5 py-0.5">
            {group.entries.length}
          </span>
        </div>
        <span className="text-sm font-semibold">€{group.total.toFixed(2)}</span>
      </button>

      {open && (
        <div className="divide-y">
          {group.entries.map((e) => (
            <div
              key={e.id}
              className="flex items-start justify-between px-4 py-2.5"
            >
              <div className="flex items-start gap-2">
                <span className="mt-1.5 h-2 w-2 rounded-full bg-destructive shrink-0" />
                <div>
                  <p className="text-sm font-medium">{e.category}</p>
                  {e.note && (
                    <p className="text-xs text-muted-foreground">{e.note}</p>
                  )}
                </div>
              </div>
              <span className="text-sm font-medium shrink-0 ml-4">
                €{Number(e.amount).toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function ExpenseHistory() {
  const { data: expenses = [], isLoading } = useAllExpenses()

  if (isLoading) {
    return (
      <div className="flex flex-col gap-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-14 bg-muted animate-pulse rounded-lg" />
        ))}
      </div>
    )
  }

  if (expenses.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-8">
        No expenses logged yet.
      </p>
    )
  }

  const groups = groupByDate(expenses)

  return (
    <div className="flex flex-col gap-2">
      {groups.map((group) => (
        <DateGroupRow key={group.date} group={group} />
      ))}
    </div>
  )
}
