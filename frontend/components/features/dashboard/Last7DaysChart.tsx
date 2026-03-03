"use client"

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Props {
  data: (number | null)[]
}

function dayLabel(daysAgo: number): string {
  const d = new Date()
  d.setDate(d.getDate() - daysAgo)
  return d.toLocaleDateString("en-US", { weekday: "short" })
}

export function Last7DaysChart({ data }: Props) {
  const chartData = data.map((score, i) => ({
    day: dayLabel(6 - i),
    score: score ?? 0,
    hasData: score !== null,
  }))

  return (
    <Card className="col-span-full lg:col-span-2">
      <CardHeader>
        <CardTitle className="text-sm font-medium">Integrity — Last 7 Days</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={chartData} barSize={28}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="day" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 100]} hide />
            <Tooltip
              formatter={(value, _name, item) => [
                item.payload?.hasData ? `${value}%` : "No entry",
                "Score",
              ]}
              cursor={{ fill: "hsl(var(--muted))" }}
            />
            <Bar
              dataKey="score"
              radius={[4, 4, 0, 0]}
              fill="hsl(var(--primary))"
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
