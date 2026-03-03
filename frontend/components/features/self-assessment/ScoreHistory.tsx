"use client"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"
import type { SelfAssessmentHistoryResponse } from "@/types/self-assessment"

interface Props {
  history: SelfAssessmentHistoryResponse
}

export function ScoreHistory({ history }: Props) {
  // Reverse to show oldest → newest on x-axis
  const data = [...history.entries].reverse().map((e) => ({
    date: e.date.slice(5), // MM-DD
    score: e.integrity_score,
  }))

  if (data.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-4">
        No history yet
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">30-day average</span>
        <span className="font-semibold">{history.average_score}%</span>
      </div>
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10 }}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} tickLine={false} />
          <Tooltip
            formatter={(v: number | undefined) => [`${v ?? 0}%`, "Score"]}
            labelStyle={{ fontSize: 11 }}
            contentStyle={{ fontSize: 11 }}
          />
          <ReferenceLine y={50} stroke="#e2e8f0" strokeDasharray="4 2" />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#6366f1"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
