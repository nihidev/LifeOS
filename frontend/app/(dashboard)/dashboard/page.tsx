"use client"

import { Trophy } from "lucide-react"
import { useDashboard } from "@/hooks/useDashboard"
import { IntegrityScoreCard } from "@/components/features/dashboard/IntegrityScoreCard"
import { WorkoutStreakCard } from "@/components/features/dashboard/WorkoutStreakCard"
import { ExpenseSummaryCard } from "@/components/features/dashboard/ExpenseSummaryCard"
import { ResolutionProgressCard } from "@/components/features/dashboard/ResolutionProgressCard"
import { Last7DaysChart } from "@/components/features/dashboard/Last7DaysChart"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div>
        <Skeleton className="h-8 w-48 mb-1" />
        <Skeleton className="h-4 w-64" />
      </div>
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-32 rounded-lg" />
        ))}
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data, isLoading, isError } = useDashboard()

  if (isLoading) return <DashboardSkeleton />

  if (isError || !data) {
    return (
      <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
        Failed to load dashboard data. Make sure the backend is running.
      </div>
    )
  }

  const today = new Date(data.date + "T00:00:00").toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">{today}</p>
      </div>

      {/* Today at a glance */}
      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Today at a glance
        </h2>
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
          {/* Small wins */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Small Wins</CardTitle>
              <Trophy className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-500">{data.small_wins_today}</div>
              <p className="text-xs text-muted-foreground mt-1">Wins logged today</p>
            </CardContent>
          </Card>

          <IntegrityScoreCard score={data.integrity_score_today} />
          <WorkoutStreakCard streak={data.workout_streak} didWorkoutToday={data.did_workout_today} />
          <ResolutionProgressCard
            active={data.active_resolutions}
            completed={data.completed_resolutions}
          />
        </div>
      </section>

      {/* Expenses + chart */}
      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Finance & Trends
        </h2>
        <div className="grid gap-4 grid-cols-1 lg:grid-cols-3">
          <ExpenseSummaryCard
            total={data.monthly_expense_total}
            summary={data.expense_summary_this_month}
          />
          <Last7DaysChart data={data.last_7_days_integrity} />
        </div>
      </section>
    </div>
  )
}
