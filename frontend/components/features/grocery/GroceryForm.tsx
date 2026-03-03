"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useAddGroceryItem } from "@/hooks/useGrocery"

export function GroceryForm() {
  const [item, setItem] = useState("")
  const [quantity, setQuantity] = useState("")

  const add = useAddGroceryItem()

  const isValid = item.trim().length > 0

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isValid) return
    try {
      await add.mutateAsync({
        item: item.trim(),
        quantity: quantity.trim() || undefined,
      })
      setItem("")
      setQuantity("")
    } catch {
      // error handled by React Query
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        placeholder="Item (e.g. Oat milk)"
        value={item}
        onChange={(e) => setItem(e.target.value)}
        className="flex-1"
      />
      <Input
        placeholder="Qty (optional)"
        value={quantity}
        onChange={(e) => setQuantity(e.target.value)}
        className="w-36 shrink-0"
      />
      <Button type="submit" disabled={!isValid || add.isPending}>
        Add
      </Button>
    </form>
  )
}
