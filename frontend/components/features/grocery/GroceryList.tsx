"use client"

import { Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { useUpdateGroceryItem, useDeleteGroceryItem, useClearChecked } from "@/hooks/useGrocery"
import type { GroceryItemResponse } from "@/types/grocery"

interface GroceryListProps {
  items: GroceryItemResponse[]
}

interface GroceryItemRowProps {
  item: GroceryItemResponse
}

function GroceryItemRow({ item }: GroceryItemRowProps) {
  const update = useUpdateGroceryItem()
  const remove = useDeleteGroceryItem()

  function handleCheck(checked: boolean) {
    update.mutate({ id: item.id, body: { checked } })
  }

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border bg-card">
      <Checkbox
        checked={item.checked}
        onCheckedChange={(v) => handleCheck(v === true)}
        disabled={update.isPending}
        aria-label={`Mark "${item.item}" as ${item.checked ? "unchecked" : "checked"}`}
      />
      <div className="flex-1 min-w-0">
        <span
          className={`text-sm font-medium ${
            item.checked ? "line-through text-muted-foreground" : ""
          }`}
        >
          {item.item}
        </span>
        {item.quantity && (
          <span className="ml-2 text-xs text-muted-foreground">{item.quantity}</span>
        )}
      </div>
      <Button
        size="icon"
        variant="ghost"
        className="h-7 w-7 shrink-0"
        onClick={() => remove.mutate({ id: item.id })}
        disabled={remove.isPending}
        aria-label="Delete item"
      >
        <Trash2 className="h-3.5 w-3.5 text-destructive" />
      </Button>
    </div>
  )
}

export function GroceryList({ items }: GroceryListProps) {
  const clearChecked = useClearChecked()

  const checkedCount = items.filter((i) => i.checked).length

  if (items.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-6">
        Your grocery list is empty. Add an item above.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-2">
        {items.map((item) => (
          <GroceryItemRow key={item.id} item={item} />
        ))}
      </div>
      {checkedCount > 0 && (
        <Button
          variant="outline"
          size="sm"
          className="self-end text-muted-foreground"
          onClick={() => clearChecked.mutate()}
          disabled={clearChecked.isPending}
        >
          Clear {checkedCount} checked {checkedCount === 1 ? "item" : "items"}
        </Button>
      )}
    </div>
  )
}
