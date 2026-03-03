"use client"

import type { CheckInResponse } from "@/types/resolution"

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

function ratingColor(rating: number): string {
  if (rating <= 2) return "bg-red-300"
  if (rating === 3) return "bg-yellow-400"
  return "bg-green-500"
}

interface MonthHeatmapProps {
  checkIns: CheckInResponse[]
  onClickMonth: (year: number, month: number) => void
}

export function MonthHeatmap({ checkIns, onClickMonth }: MonthHeatmapProps) {
  const year = new Date().getFullYear()

  const byMonth: Record<number, CheckInResponse> = {}
  for (const ci of checkIns) {
    if (ci.year === year) {
      byMonth[ci.month] = ci
    }
  }

  return (
    <div className="flex gap-1 flex-wrap">
      {MONTHS.map((label, idx) => {
        const month = idx + 1
        const ci = byMonth[month]
        const dotColor = ci ? ratingColor(ci.rating) : "bg-muted"

        return (
          <button
            key={month}
            onClick={() => onClickMonth(year, month)}
            className="flex flex-col items-center gap-0.5 group"
            title={ci ? `Rating: ${ci.rating}` : "No check-in"}
          >
            <div
              className={`w-5 h-5 rounded-full ${dotColor} group-hover:ring-2 group-hover:ring-primary/50 transition-all`}
            />
            <span className="text-[10px] text-muted-foreground">{label}</span>
          </button>
        )
      })}
    </div>
  )
}
