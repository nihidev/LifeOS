"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { SmallWinForm } from "@/components/features/small-wins/SmallWinForm"
import { SmallWinList } from "@/components/features/small-wins/SmallWinList"
import { WinStreakBanner } from "@/components/features/small-wins/WinStreakBanner"
import { useSmallWins } from "@/hooks/useSmallWins"
import { getToday, formatDate, cn } from "@/lib/utils"
import type { SmallWinCategory } from "@/types/small-win"

const CATEGORIES: SmallWinCategory[] = ["Work", "Health", "Personal Growth", "General"]

function shiftDate(dateStr: string, days: number): string {
  const [y, m, d] = dateStr.split("-").map(Number)
  return new Date(Date.UTC(y, m - 1, d + days)).toISOString().slice(0, 10)
}

export default function SmallWinsPage() {
  const [date, setDate] = useState(getToday())
  const [activeFilter, setActiveFilter] = useState<SmallWinCategory | null>(null)
  const today = getToday()
  const { data: wins, isLoading, isError } = useSmallWins(date)

  const filteredWins = wins
    ? wins.filter((w) => !activeFilter || w.category === activeFilter)
    : []

  const winCount =
    wins?.filter((w) => w.entry_type === "win" || w.completed === true).length ?? 0

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        {/* Header + date navigator */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Small Wins</h1>
          <div className="flex items-center gap-2">
            <Button
              size="icon"
              variant="outline"
              onClick={() => setDate((d) => shiftDate(d, -1))}
              aria-label="Previous day"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm font-medium w-28 text-center">
              {date === today ? "Today" : formatDate(date)}
            </span>
            <Button
              size="icon"
              variant="outline"
              onClick={() => setDate((d) => shiftDate(d, 1))}
              aria-label="Next day"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Streak + heatmap banner */}
        <WinStreakBanner />

        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {date === today ? "Log a Win or Task" : `Plan for ${formatDate(date)}`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SmallWinForm date={date} />
          </CardContent>
        </Card>

        {/* List section */}
        <div>
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
              {winCount} Win{winCount === 1 ? "" : "s"} Today
            </h2>

            {/* Category filter pills */}
            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() => setActiveFilter(null)}
                className={cn(
                  "px-2.5 py-1 rounded-full text-xs font-medium border transition-colors",
                  activeFilter === null
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-background text-muted-foreground border-border hover:border-foreground"
                )}
              >
                All
              </button>
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setActiveFilter((prev) => (prev === cat ? null : cat))}
                  className={cn(
                    "px-2.5 py-1 rounded-full text-xs font-medium border transition-colors",
                    activeFilter === cat
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background text-muted-foreground border-border hover:border-foreground"
                  )}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {isLoading && (
            <div className="flex flex-col gap-3">
              {[1, 2].map((i) => (
                <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          )}
          {isError && (
            <p className="text-sm text-destructive text-center py-8">
              Failed to load wins. Please refresh.
            </p>
          )}
          {wins && <SmallWinList wins={filteredWins} date={date} />}
        </div>
      </div>
    </PageWrapper>
  )
}
