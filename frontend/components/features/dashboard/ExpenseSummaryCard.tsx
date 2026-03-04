import { CreditCard } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Props {
  total: string
  summary: Record<string, string>
}

export function ExpenseSummaryCard({ total, summary }: Props) {
  const entries = Object.entries(summary).sort(
    ([, a], [, b]) => parseFloat(b) - parseFloat(a)
  )

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Monthly Expenses</CardTitle>
        <CreditCard className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">€{parseFloat(total).toFixed(2)}</div>
        <p className="text-xs text-muted-foreground mt-1">This month</p>
        {entries.length > 0 && (
          <ul className="mt-3 space-y-1">
            {entries.slice(0, 3).map(([cat, amt]) => (
              <li key={cat} className="flex justify-between text-xs">
                <span className="text-muted-foreground">{cat}</span>
                <span className="font-medium">€{parseFloat(amt).toFixed(2)}</span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
