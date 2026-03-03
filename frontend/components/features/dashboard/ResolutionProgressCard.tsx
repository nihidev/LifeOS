import { Target } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Props {
  active: number
  completed: number
}

export function ResolutionProgressCard({ active, completed }: Props) {
  const total = active + completed
  const completionPct = total > 0 ? Math.round((completed / total) * 100) : 0

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Resolutions</CardTitle>
        <Target className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{active}</div>
        <p className="text-xs text-muted-foreground mt-1">active</p>
        <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
          <span>{completed} completed</span>
          {total > 0 && <span>·</span>}
          {total > 0 && <span>{completionPct}% done</span>}
        </div>
      </CardContent>
    </Card>
  )
}
