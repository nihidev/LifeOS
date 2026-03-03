"use client"

import { Minus, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useWater, useWaterIncrement, useWaterDecrement } from "@/hooks/useFoodLogs"

interface WaterCounterProps {
  date: string
}

export function WaterCounter({ date }: WaterCounterProps) {
  const { data } = useWater(date)
  const increment = useWaterIncrement()
  const decrement = useWaterDecrement()

  const glasses = data?.glasses ?? 0

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-1">
        {Array.from({ length: 8 }).map((_, i) => (
          <span
            key={i}
            className={`text-lg transition-opacity ${
              i < glasses ? "opacity-100" : "opacity-20"
            }`}
            aria-hidden
          >
            💧
          </span>
        ))}
      </div>
      <div className="flex items-center gap-2 ml-auto">
        <Button
          size="icon"
          variant="outline"
          className="h-8 w-8"
          onClick={() => decrement.mutate({ date })}
          disabled={glasses === 0 || decrement.isPending}
          aria-label="Remove glass"
        >
          <Minus className="h-3.5 w-3.5" />
        </Button>
        <span className="text-sm font-semibold w-6 text-center">{glasses}</span>
        <Button
          size="icon"
          variant="outline"
          className="h-8 w-8"
          onClick={() => increment.mutate({ date })}
          disabled={increment.isPending}
          aria-label="Add glass"
        >
          <Plus className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  )
}
