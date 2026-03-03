"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { ExpenseForm } from "@/components/features/expenses/ExpenseForm"
import { ExpenseList } from "@/components/features/expenses/ExpenseList"
import { CategoryBreakdown } from "@/components/features/expenses/CategoryBreakdown"
import { ExpenseHistory } from "@/components/features/expenses/ExpenseHistory"
import {
  useExpenses,
  useWeeklySummary,
  useMonthlySummary,
  useCumulativeSummary,
} from "@/hooks/useExpenses"
import { getToday, formatDate } from "@/lib/utils"

function shiftDate(dateStr: string, days: number): string {
  const [y, m, d] = dateStr.split("-").map(Number)
  return new Date(Date.UTC(y, m - 1, d + days)).toISOString().slice(0, 10)
}

type SummaryTab = "weekly" | "monthly" | "cumulative"
type ViewTab = "day" | "history"

export default function ExpensesPage() {
  const today = getToday()
  const [date, setDate] = useState(today)
  const now = new Date()
  const [calYear, setCalYear] = useState(now.getFullYear())
  const [calMonth, setCalMonth] = useState(now.getMonth() + 1)
  const [summaryTab, setSummaryTab] = useState<SummaryTab>("weekly")
  const [viewTab, setViewTab] = useState<ViewTab>("day")

  const { data: expenses = [], isLoading } = useExpenses(date)
  const { data: weekly } = useWeeklySummary(date)
  const { data: monthly } = useMonthlySummary(calYear, calMonth)
  const { data: cumulative } = useCumulativeSummary()

  function prevMonth() {
    if (calMonth === 1) { setCalMonth(12); setCalYear((y) => y - 1) }
    else setCalMonth((m) => m - 1)
  }

  function nextMonth() {
    const isCurrentMonth =
      calYear === now.getFullYear() && calMonth === now.getMonth() + 1
    if (isCurrentMonth) return
    if (calMonth === 12) { setCalMonth(1); setCalYear((y) => y + 1) }
    else setCalMonth((m) => m + 1)
  }

  const isCurrentMonth =
    calYear === now.getFullYear() && calMonth === now.getMonth() + 1

  const activeSummary =
    summaryTab === "weekly"
      ? weekly
      : summaryTab === "monthly"
      ? monthly
      : cumulative

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Expenses</h1>
          <div className="flex items-center gap-2">
            {/* View toggle */}
            <div className="flex rounded-lg border overflow-hidden text-sm">
              <button
                className={`px-3 py-1.5 transition-colors ${
                  viewTab === "day"
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                }`}
                onClick={() => setViewTab("day")}
              >
                Day
              </button>
              <button
                className={`px-3 py-1.5 transition-colors ${
                  viewTab === "history"
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                }`}
                onClick={() => setViewTab("history")}
              >
                History
              </button>
            </div>
            {/* Date nav (only in day view) */}
            {viewTab === "day" && (
              <>
                <Button
                  size="icon"
                  variant="outline"
                  onClick={() => setDate((d) => shiftDate(d, -1))}
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
                  disabled={date >= today}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Day view */}
        {viewTab === "day" && (
          <>
            {/* Add form */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  {date === today ? "Add Expense" : `Add for ${formatDate(date)}`}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ExpenseForm date={date} />
              </CardContent>
            </Card>

            {/* Daily list */}
            <Card>
              <CardContent className="pt-5">
                {isLoading ? (
                  <div className="flex flex-col gap-2">
                    {[1, 2].map((i) => (
                      <div key={i} className="h-14 bg-muted animate-pulse rounded-lg" />
                    ))}
                  </div>
                ) : (
                  <ExpenseList expenses={expenses} date={date} />
                )}
              </CardContent>
            </Card>

            {/* Summary */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Summary</CardTitle>
                  {/* Monthly nav only visible when monthly tab active */}
                  {summaryTab === "monthly" && (
                    <div className="flex items-center gap-1">
                      <Button size="icon" variant="ghost" onClick={prevMonth}>
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <span className="text-xs text-muted-foreground w-24 text-center">
                        {new Date(calYear, calMonth - 1).toLocaleString("default", {
                          month: "short",
                          year: "numeric",
                        })}
                      </span>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={nextMonth}
                        disabled={isCurrentMonth}
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
                {/* Tab strip */}
                <div className="flex gap-1 mt-1">
                  {(["weekly", "monthly", "cumulative"] as SummaryTab[]).map((t) => (
                    <button
                      key={t}
                      onClick={() => setSummaryTab(t)}
                      className={`text-xs px-3 py-1 rounded-full font-medium transition-colors ${
                        summaryTab === t
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      {t.charAt(0).toUpperCase() + t.slice(1)}
                    </button>
                  ))}
                </div>
                {activeSummary && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Total: <span className="font-semibold text-foreground">€{Number(activeSummary.total).toFixed(2)}</span>
                  </p>
                )}
              </CardHeader>
              <CardContent>
                {activeSummary ? (
                  <CategoryBreakdown summary={activeSummary} />
                ) : (
                  <div className="h-32 bg-muted animate-pulse rounded-md" />
                )}
              </CardContent>
            </Card>
          </>
        )}

        {/* History view */}
        {viewTab === "history" && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">All Expenses</CardTitle>
            </CardHeader>
            <CardContent>
              <ExpenseHistory />
            </CardContent>
          </Card>
        )}
      </div>
    </PageWrapper>
  )
}
