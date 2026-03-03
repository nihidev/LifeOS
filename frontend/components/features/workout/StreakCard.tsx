import { Flame, Trophy } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import type { StreakResponse } from "@/types/workout"

interface StreakCardProps {
  streak: StreakResponse
}

export function StreakCard({ streak }: StreakCardProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <Card>
        <CardContent className="pt-6 flex flex-col items-center gap-1">
          <Flame
            className={`h-8 w-8 ${streak.current_streak > 0 ? "text-orange-500" : "text-muted-foreground"}`}
          />
          <span className="text-3xl font-bold">{streak.current_streak}</span>
          <span className="text-xs text-muted-foreground uppercase tracking-wide">
            Current Streak
          </span>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6 flex flex-col items-center gap-1">
          <Trophy className="h-8 w-8 text-yellow-500" />
          <span className="text-3xl font-bold">{streak.longest_streak}</span>
          <span className="text-xs text-muted-foreground uppercase tracking-wide">
            Longest Streak
          </span>
        </CardContent>
      </Card>
    </div>
  )
}
