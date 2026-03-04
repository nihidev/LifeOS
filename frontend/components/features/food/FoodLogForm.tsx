"use client"

import { useState } from "react"
import { Plus, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useAddFoodLog } from "@/hooks/useFoodLogs"
import { toast } from "sonner"

interface FoodLogFormProps {
  date: string
}

export function FoodLogForm({ date }: FoodLogFormProps) {
  const [time, setTime] = useState(() => {
    const now = new Date()
    return `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`
  })
  const [dishes, setDishes] = useState<string[]>([""])

  const add = useAddFoodLog()

  const validDishes = dishes.filter((d) => d.trim().length > 0)
  const isValid = time.length > 0 && validDishes.length > 0

  function handleDishChange(index: number, value: string) {
    setDishes((prev) => prev.map((d, i) => (i === index ? value : d)))
  }

  function addDish() {
    setDishes((prev) => [...prev, ""])
  }

  function removeDish(index: number) {
    setDishes((prev) => prev.filter((_, i) => i !== index))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isValid) return
    try {
      await Promise.all(
        validDishes.map((dish) =>
          add.mutateAsync({ date, consumed_at: time, food_item: dish.trim() })
        )
      )
      setDishes([""])
    } catch {
      toast.error("Failed to log food")
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      {/* Meal time */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground w-12 shrink-0">Time</span>
        <Input
          type="time"
          value={time}
          onChange={(e) => setTime(e.target.value)}
          className="w-36"
          required
        />
      </div>

      {/* Dishes */}
      <div className="flex flex-col gap-2">
        <span className="text-sm text-muted-foreground">Dishes</span>
        {dishes.map((dish, i) => (
          <div key={i} className="flex gap-2 items-center">
            <Input
              placeholder={i === 0 ? "e.g. Oatmeal with berries" : "e.g. Coffee"}
              value={dish}
              onChange={(e) => handleDishChange(i, e.target.value)}
              className="flex-1"
              autoFocus={i === dishes.length - 1 && i > 0}
            />
            {dishes.length > 1 && (
              <Button
                type="button"
                size="icon"
                variant="ghost"
                className="h-9 w-9 shrink-0"
                onClick={() => removeDish(i)}
                aria-label="Remove dish"
              >
                <X className="h-4 w-4 text-muted-foreground" />
              </Button>
            )}
          </div>
        ))}

        <button
          type="button"
          onClick={addDish}
          className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors self-start mt-0.5"
        >
          <Plus className="h-3.5 w-3.5" />
          Add another dish
        </button>
      </div>

      <Button
        type="submit"
        disabled={!isValid || add.isPending}
        className="self-end"
      >
        {add.isPending ? "Logging…" : `Log ${validDishes.length > 1 ? `${validDishes.length} dishes` : "meal"}`}
      </Button>
    </form>
  )
}
