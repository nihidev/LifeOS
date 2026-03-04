"use client"

import { Skeleton } from "@/components/ui/skeleton"
import { useSmallWinStats } from "@/hooks/useSmallWins"
import { cn } from "@/lib/utils"
import { getToday } from "@/lib/utils"

const DAY_LABELS = ["M", "T", "W", "T", "F", "S", "S"]

const MILESTONES = [10, 25, 50, 100, 250, 500, 1000]

function getMilestoneInfo(total: number) {
  const next = MILESTONES.find((m) => total < m) ?? null
  const prev = next ? (MILESTONES[MILESTONES.indexOf(next) - 1] ?? 0) : MILESTONES[MILESTONES.length - 1]
  const progress = next ? (total - prev) / (next - prev) : 1
  return { next, prev, progress }
}

function milestoneLabel(total: number, next: number | null): string {
  if (next === null) return "Legend status 🏆"
  return `${next - total} to ${next}`
}

function heatmapColor(count: number): string {
  if (count === 0) return "bg-muted"
  if (count === 1) return "bg-green-200"
  if (count === 2) return "bg-green-400"
  return "bg-green-600"
}

export function WinStreakBanner() {
  const { data: stats, isLoading } = useSmallWinStats()
  const today = getToday()

  if (isLoading) {
    return (
      <div className="flex items-center justify-between rounded-xl border bg-card p-4">
        <Skeleton className="h-12 w-36" />
        <Skeleton className="h-10 w-48" />
      </div>
    )
  }

  if (!stats) return null

  const { total_wins, wins_last_7_days } = stats
  const { next, prev, progress } = getMilestoneInfo(total_wins)

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 rounded-xl border bg-card p-4">
      {/* Milestone counter */}
      <div className="flex flex-col gap-1.5 min-w-0">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold tabular-nums">{total_wins}</span>
          <span className="text-sm text-muted-foreground font-medium">total wins</span>
        </div>
        {/* Progress bar */}
        <div className="flex items-center gap-2">
          <div className="h-1.5 w-32 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full rounded-full bg-green-500 transition-all duration-500"
              style={{ width: `${Math.round(progress * 100)}%` }}
            />
          </div>
          <span className="text-xs text-muted-foreground whitespace-nowrap">
            {milestoneLabel(total_wins, next)}
          </span>
        </div>
      </div>

      {/* 7-day heatmap */}
      <div className="flex gap-2">
        {wins_last_7_days.map((day, i) => {
          const isToday = day.date === today
          return (
            <div key={day.date} className="flex flex-col items-center gap-1">
              <div
                className={cn(
                  "h-7 w-7 rounded-full",
                  heatmapColor(day.count),
                  isToday && "ring-2 ring-green-600 ring-offset-1"
                )}
                title={`${day.date}: ${day.count} win${day.count === 1 ? "" : "s"}`}
              />
              <span className="text-[10px] text-muted-foreground leading-none">
                {DAY_LABELS[i]}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
