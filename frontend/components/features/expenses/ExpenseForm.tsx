"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useAddExpense } from "@/hooks/useExpenses"
import { EXPENSE_CATEGORIES } from "@/types/expense"
import type { ExpenseCategory } from "@/types/expense"

interface ExpenseFormProps {
  date: string
}

export function ExpenseForm({ date }: ExpenseFormProps) {
  const [amount, setAmount] = useState("")
  const [category, setCategory] = useState<ExpenseCategory | "">("")
  const [note, setNote] = useState("")

  const add = useAddExpense()

  const isValid = parseFloat(amount) > 0 && category !== ""

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isValid) return
    try {
      await add.mutateAsync({
        date,
        amount: parseFloat(parseFloat(amount).toFixed(2)),
        category: category as ExpenseCategory,
        note: note.trim() || undefined,
      })
      setAmount("")
      setCategory("")
      setNote("")
    } catch {
      // error handled by React Query
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground font-medium">
            €
          </span>
          <Input
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="pl-7"
          />
        </div>
        <Select
          value={category}
          onValueChange={(v) => setCategory(v as ExpenseCategory)}
        >
          <SelectTrigger className="flex-1">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            {EXPENSE_CATEGORIES.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex gap-2">
        <Input
          placeholder="Note (optional)"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          className="flex-1"
        />
        <Button type="submit" disabled={!isValid || add.isPending}>
          Add
        </Button>
      </div>
    </form>
  )
}
