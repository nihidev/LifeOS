import { Brain } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Props {
  score: number | null
}

export function IntegrityScoreCard({ score }: Props) {
  const display = score === null ? "—" : `${score}%`
  const color =
    score === null
      ? "text-muted-foreground"
      : score === 100
      ? "text-green-500"
      : score >= 50
      ? "text-yellow-500"
      : "text-red-500"

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Integrity Score</CardTitle>
        <Brain className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className={`text-3xl font-bold ${color}`}>{display}</div>
        <p className="text-xs text-muted-foreground mt-1">Today's self assessment</p>
      </CardContent>
    </Card>
  )
}
