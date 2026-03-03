"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { FoodLogForm } from "@/components/features/food/FoodLogForm"
import { FoodLogList } from "@/components/features/food/FoodLogList"
import { WaterCounter } from "@/components/features/food/WaterCounter"
import { useFoodLogs } from "@/hooks/useFoodLogs"
import { getToday, formatDate } from "@/lib/utils"

function shiftDate(dateStr: string, days: number): string {
  const [y, m, d] = dateStr.split("-").map(Number)
  return new Date(Date.UTC(y, m - 1, d + days)).toISOString().slice(0, 10)
}

export default function FoodPage() {
  const today = getToday()
  const [date, setDate] = useState(today)

  const { data: entries = [], isLoading } = useFoodLogs(date)

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Food Log</h1>
          <div className="flex items-center gap-2">
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
          </div>
        </div>

        {/* Water counter */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Water Intake</CardTitle>
          </CardHeader>
          <CardContent>
            <WaterCounter date={date} />
          </CardContent>
        </Card>

        {/* Add food log */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {date === today ? "Log a Meal" : `Log for ${formatDate(date)}`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <FoodLogForm date={date} />
          </CardContent>
        </Card>

        {/* Meal list */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {date === today ? "Today's Meals" : `Meals on ${formatDate(date)}`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex flex-col gap-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />
                ))}
              </div>
            ) : (
              <FoodLogList entries={entries} date={date} />
            )}
          </CardContent>
        </Card>
      </div>
    </PageWrapper>
  )
}
