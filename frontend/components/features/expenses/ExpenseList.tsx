"use client"

import { useState } from "react"
import { Pencil, Trash2, Check, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useDeleteExpense, useUpdateExpense } from "@/hooks/useExpenses"
import type { ExpenseCategory, ExpenseResponse } from "@/types/expense"
import { EXPENSE_CATEGORIES } from "@/types/expense"

interface ExpenseListProps {
  expenses: ExpenseResponse[]
  date: string
}

interface ExpenseItemProps {
  expense: ExpenseResponse
  date: string
}

function ExpenseItem({ expense, date }: ExpenseItemProps) {
  const [editing, setEditing] = useState(false)
  const [draftAmount, setDraftAmount] = useState(String(expense.amount))
  const [draftCategory, setDraftCategory] = useState<ExpenseCategory>(
    expense.category
  )
  const [draftNote, setDraftNote] = useState(expense.note ?? "")

  const update = useUpdateExpense()
  const remove = useDeleteExpense()

  async function handleSave() {
    const amt = parseFloat(draftAmount)
    if (!amt || amt <= 0) {
      setEditing(false)
      return
    }
    try {
      await update.mutateAsync({
        id: expense.id,
        date,
        body: {
          amount: parseFloat(amt.toFixed(2)),
          category: draftCategory,
          note: draftNote.trim() || undefined,
        },
      })
      setEditing(false)
    } catch {
      // error surfaced via React Query
    }
  }

  function handleCancel() {
    setDraftAmount(String(expense.amount))
    setDraftCategory(expense.category)
    setDraftNote(expense.note ?? "")
    setEditing(false)
  }

  if (editing) {
    return (
      <div className="flex items-center gap-2 p-3 rounded-lg border bg-card">
        <div className="relative w-28">
          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
            €
          </span>
          <Input
            type="number"
            step="0.01"
            min="0.01"
            value={draftAmount}
            onChange={(e) => setDraftAmount(e.target.value)}
            className="pl-5 h-8 text-sm"
            autoFocus
          />
        </div>
        <Select
          value={draftCategory}
          onValueChange={(v) => setDraftCategory(v as ExpenseCategory)}
        >
          <SelectTrigger className="flex-1 h-8 text-sm">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {EXPENSE_CATEGORIES.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input
          placeholder="Note"
          value={draftNote}
          onChange={(e) => setDraftNote(e.target.value)}
          className="flex-1 h-8 text-sm"
        />
        <Button
          size="icon"
          variant="ghost"
          className="h-8 w-8"
          onClick={handleSave}
          disabled={update.isPending}
          aria-label="Save"
        >
          <Check className="h-4 w-4 text-green-600" />
        </Button>
        <Button
          size="icon"
          variant="ghost"
          className="h-8 w-8"
          onClick={handleCancel}
          aria-label="Cancel"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border bg-card">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{expense.category}</span>
        </div>
        {expense.note && (
          <p className="text-xs text-muted-foreground truncate">{expense.note}</p>
        )}
      </div>
      <span className="text-sm font-semibold shrink-0">
        €{Number(expense.amount).toFixed(2)}
      </span>
      <div className="flex gap-1 shrink-0">
        <Button
          size="icon"
          variant="ghost"
          className="h-7 w-7"
          onClick={() => setEditing(true)}
          aria-label="Edit"
        >
          <Pencil className="h-3.5 w-3.5" />
        </Button>
        <Button
          size="icon"
          variant="ghost"
          className="h-7 w-7"
          onClick={() => remove.mutate({ id: expense.id, date })}
          disabled={remove.isPending}
          aria-label="Delete"
        >
          <Trash2 className="h-3.5 w-3.5 text-destructive" />
        </Button>
      </div>
    </div>
  )
}

export function ExpenseList({ expenses, date }: ExpenseListProps) {
  const total = expenses.reduce((sum, e) => sum + Number(e.amount), 0)

  if (expenses.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-6">
        No expenses logged for this day.
      </p>
    )
  }

  return (
    <div>
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
        {expenses.length} expense{expenses.length === 1 ? "" : "s"} · €
        {total.toFixed(2)}
      </p>
      <div className="flex flex-col gap-2">
        {expenses.map((e) => (
          <ExpenseItem key={e.id} expense={e} date={date} />
        ))}
      </div>
    </div>
  )
}
