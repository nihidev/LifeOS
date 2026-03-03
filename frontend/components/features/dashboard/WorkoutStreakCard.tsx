import { Dumbbell, Flame } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface Props {
  streak: number
  didWorkoutToday: boolean
}

export function WorkoutStreakCard({ streak, didWorkoutToday }: Props) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Workout Streak</CardTitle>
        <Dumbbell className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2">
          <span className="text-3xl font-bold">{streak}</span>
          {streak > 0 && <Flame className="h-6 w-6 text-orange-500" />}
        </div>
        <div className="mt-1 flex items-center gap-2">
          <p className="text-xs text-muted-foreground">
            {streak === 1 ? "day" : "days"} in a row
          </p>
          <Badge
            variant={didWorkoutToday ? "default" : "secondary"}
            className="text-xs"
          >
            {didWorkoutToday ? "Done today" : "Not yet today"}
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}
