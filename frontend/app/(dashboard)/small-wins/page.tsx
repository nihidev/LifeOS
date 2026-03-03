"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { SmallWinForm } from "@/components/features/small-wins/SmallWinForm"
import { SmallWinList } from "@/components/features/small-wins/SmallWinList"
import { useSmallWins } from "@/hooks/useSmallWins"
import { getToday, formatDate } from "@/lib/utils"

function shiftDate(dateStr: string, days: number): string {
  const [y, m, d] = dateStr.split("-").map(Number)
  return new Date(Date.UTC(y, m - 1, d + days)).toISOString().slice(0, 10)
}

export default function SmallWinsPage() {
  const [date, setDate] = useState(getToday())
  const today = getToday()
  const { data: wins, isLoading, isError } = useSmallWins(date)

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto flex flex-col gap-6">
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

        <div>
          {(() => {
            const winCount = wins?.filter(
              (w) => w.entry_type === "win" || w.completed === true
            ).length ?? 0
            return (
              <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                {winCount} Win{winCount === 1 ? "" : "s"} Logged
              </h2>
            )
          })()}
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
          {wins && <SmallWinList wins={wins} date={date} />}
        </div>
      </div>
    </PageWrapper>
  )
}
