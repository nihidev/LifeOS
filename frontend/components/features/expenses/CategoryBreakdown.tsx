"use client"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts"
import type { SummaryResponse } from "@/types/expense"

interface CategoryBreakdownProps {
  summary: SummaryResponse
}

export function CategoryBreakdown({ summary }: CategoryBreakdownProps) {
  if (summary.by_category.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-8">
        No expenses logged for this period.
      </p>
    )
  }

  const chartData = [...summary.by_category]
    .sort((a, b) => Number(a.total) - Number(b.total))
    .map((item) => ({
      category: item.category,
      total: Number(item.total),
    }))

  return (
    <div className="flex flex-col gap-4">
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 0, right: 16, bottom: 0, left: 0 }}
          >
            <XAxis
              type="number"
              tick={{ fontSize: 11 }}
              tickFormatter={(v: number) => `€${v}`}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="category"
              width={100}
              tick={{ fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              formatter={(value: number | undefined) =>
                value != null ? [`€${value.toFixed(2)}`, "Total"] : ["-", "Total"]
              }
              cursor={{ fill: "hsl(var(--muted))" }}
            />
            <Bar dataKey="total" radius={[0, 4, 4, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill="hsl(var(--primary))" />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <table className="w-full text-sm">
        <thead>
          <tr className="text-xs text-muted-foreground uppercase tracking-wide border-b">
            <th className="text-left pb-2 font-medium">Category</th>
            <th className="text-right pb-2 font-medium">Total</th>
            <th className="text-right pb-2 font-medium">Entries</th>
          </tr>
        </thead>
        <tbody>
          {summary.by_category.map((item) => (
            <tr key={item.category} className="border-b last:border-0">
              <td className="py-2">{item.category}</td>
              <td className="py-2 text-right font-medium">
                €{Number(item.total).toFixed(2)}
              </td>
              <td className="py-2 text-right text-muted-foreground">
                {item.count}
              </td>
            </tr>
          ))}
          <tr className="font-semibold">
            <td className="pt-3">Total</td>
            <td className="pt-3 text-right">€{Number(summary.total).toFixed(2)}</td>
            <td />
          </tr>
        </tbody>
      </table>
    </div>
  )
}
