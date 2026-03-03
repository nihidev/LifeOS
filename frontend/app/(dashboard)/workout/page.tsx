"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { WorkoutForm } from "@/components/features/workout/WorkoutForm"
import { StreakCard } from "@/components/features/workout/StreakCard"
import { MonthlyCalendar } from "@/components/features/workout/MonthlyCalendar"
import { useWorkout, useWorkoutStreak, useWorkoutMonthlySummary } from "@/hooks/useWorkout"
import { getToday, formatDate } from "@/lib/utils"

function shiftDate(dateStr: string, days: number): string {
  const d = new Date(dateStr + "T00:00:00")
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

export default function WorkoutPage() {
  const today = getToday()
  const [date, setDate] = useState(today)
  const now = new Date()
  const [calYear, setCalYear] = useState(now.getFullYear())
  const [calMonth, setCalMonth] = useState(now.getMonth() + 1)

  const { data: workout, isLoading: loadingWorkout } = useWorkout(date)
  const { data: streak } = useWorkoutStreak()
  const { data: summary, isLoading: loadingSummary } = useWorkoutMonthlySummary(
    calYear,
    calMonth
  )

  function prevMonth() {
    if (calMonth === 1) { setCalMonth(12); setCalYear((y) => y - 1) }
    else setCalMonth((m) => m - 1)
  }

  function nextMonth() {
    const isCurrentMonth = calYear === now.getFullYear() && calMonth === now.getMonth() + 1
    if (isCurrentMonth) return
    if (calMonth === 12) { setCalMonth(1); setCalYear((y) => y + 1) }
    else setCalMonth((m) => m + 1)
  }

  const isCurrentMonth =
    calYear === now.getFullYear() && calMonth === now.getMonth() + 1

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Workout</h1>
          <div className="flex items-center gap-2">
            <Button size="icon" variant="outline" onClick={() => setDate((d) => shiftDate(d, -1))}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm font-medium w-28 text-center">
              {date === today ? "Today" : formatDate(date)}
            </span>
            <Button
              size="icon"
              variant="outline"
              onClick={() => setDate((d) => shiftDate(d, 1))}
              disabled={date >= today}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {streak && <StreakCard streak={streak} />}

        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {date === today ? "Did you workout today?" : `Log for ${formatDate(date)}`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingWorkout ? (
              <div className="h-14 bg-muted animate-pulse rounded-md" />
            ) : (
              <WorkoutForm date={date} existing={workout ?? null} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">
                {new Date(calYear, calMonth - 1).toLocaleString("default", {
                  month: "long",
                  year: "numeric",
                })}
              </CardTitle>
              <div className="flex gap-1">
                <Button size="icon" variant="ghost" onClick={prevMonth}>
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button size="icon" variant="ghost" onClick={nextMonth} disabled={isCurrentMonth}>
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
            {summary && (
              <p className="text-xs text-muted-foreground">
                {summary.workout_days}/{summary.total_days} days ·{" "}
                {summary.completion_percent}% completion
              </p>
            )}
          </CardHeader>
          <CardContent>
            {loadingSummary ? (
              <div className="h-40 bg-muted animate-pulse rounded-md" />
            ) : summary ? (
              <MonthlyCalendar
                summary={summary}
                selectedDate={date}
                onSelectDate={(d) => {
                  setDate(d)
                  const [y, m] = d.split("-").map(Number)
                  setCalYear(y)
                  setCalMonth(m)
                }}
              />
            ) : null}
          </CardContent>
        </Card>
      </div>
    </PageWrapper>
  )
}
