"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { AssessmentForm } from "@/components/features/self-assessment/AssessmentForm"
import { ScoreHistory } from "@/components/features/self-assessment/ScoreHistory"
import { useSelfAssessment, useSelfAssessmentHistory } from "@/hooks/useSelfAssessment"
import { getToday, formatDate } from "@/lib/utils"

function shiftDate(dateStr: string, days: number): string {
  const d = new Date(dateStr + "T00:00:00")
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

export default function SelfAssessmentPage() {
  const today = getToday()
  const [date, setDate] = useState(today)

  const { data: assessment, isLoading } = useSelfAssessment(date)
  const { data: history, isLoading: loadingHistory } = useSelfAssessmentHistory()

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Self Assessment</h1>
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

        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {date === today ? "Today's check-in" : `Check-in for ${formatDate(date)}`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-32 bg-muted animate-pulse rounded-md" />
            ) : (
              <AssessmentForm date={date} existing={assessment ?? null} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Integrity History</CardTitle>
          </CardHeader>
          <CardContent>
            {loadingHistory ? (
              <div className="h-40 bg-muted animate-pulse rounded-md" />
            ) : history ? (
              <ScoreHistory history={history} />
            ) : null}
          </CardContent>
        </Card>
      </div>
    </PageWrapper>
  )
}
