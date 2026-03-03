import { cn } from "@/lib/utils"
import type { MonthlySummaryResponse } from "@/types/workout"

interface MonthlyCalendarProps {
  summary: MonthlySummaryResponse
  selectedDate: string
  onSelectDate: (date: string) => void
}

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

export function MonthlyCalendar({
  summary,
  selectedDate,
  onSelectDate,
}: MonthlyCalendarProps) {
  const [year, month] = summary.month.split("-").map(Number)
  const firstDay = new Date(year, month - 1, 1).getDay()
  const totalDays = summary.total_days
  const today = new Date().toISOString().slice(0, 10)

  // Aggregate multi-entry per day
  const statusMap = new Map<string, boolean>()
  const durationMap = new Map<string, number>()
  for (const e of summary.entries) {
    statusMap.set(e.date, (statusMap.get(e.date) ?? false) || e.did_workout)
    if (e.did_workout && e.duration_mins) {
      durationMap.set(e.date, (durationMap.get(e.date) ?? 0) + e.duration_mins)
    }
  }

  const cells: (number | null)[] = [
    ...Array(firstDay).fill(null),
    ...Array.from({ length: totalDays }, (_, i) => i + 1),
  ]

  function dateStr(day: number) {
    return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`
  }

  return (
    <div>
      <div className="grid grid-cols-7 mb-1">
        {DAY_LABELS.map((d) => (
          <div key={d} className="text-center text-xs text-muted-foreground py-1">
            {d}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {cells.map((day, idx) => {
          if (!day) return <div key={`empty-${idx}`} />
          const ds = dateStr(day)
          const status = statusMap.get(ds)
          const duration = durationMap.get(ds) ?? 0
          const isFuture = ds > today
          const isSelected = ds === selectedDate
          const isToday = ds === today

          return (
            <button
              key={ds}
              onClick={() => !isFuture && onSelectDate(ds)}
              disabled={isFuture}
              className={cn(
                "rounded-md text-xs font-medium flex flex-col items-center justify-center transition-colors py-1 min-h-[2.5rem]",
                isFuture && "opacity-30 cursor-default",
                !isFuture && "hover:bg-muted cursor-pointer",
                isSelected && "ring-2 ring-primary",
                isToday && "font-bold",
                status === true && "bg-green-500/20 text-green-700 dark:text-green-400",
                status === false && "bg-red-500/10 text-red-600 dark:text-red-400",
                status === undefined && !isFuture && "text-muted-foreground"
              )}
            >
              <span>{day}</span>
              {duration > 0 && (
                <span className="text-[9px] leading-none opacity-80 font-normal">
                  {duration}m
                </span>
              )}
            </button>
          )
        })}
      </div>
      <div className="flex gap-4 justify-center mt-3 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded-sm bg-green-500/20" /> Workout
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded-sm bg-red-500/10" /> Rest
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded-sm bg-muted" /> Not logged
        </span>
      </div>
    </div>
  )
}
