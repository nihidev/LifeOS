"use client"

import type { ProgressLogResponse } from "@/types/resolution"

interface ProgressHistoryProps {
  logs: ProgressLogResponse[]
}

export function ProgressHistory({ logs }: ProgressHistoryProps) {
  if (logs.length === 0) return null

  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
        Progress History
      </p>
      <div className="flex flex-col gap-2">
        {logs.map((log) => (
          <div
            key={log.id}
            className="flex flex-col gap-0.5 rounded-md bg-muted/50 px-3 py-2"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">{log.progress_percent}%</span>
              <span className="text-xs text-muted-foreground">
                {new Date(log.logged_at).toLocaleDateString(undefined, {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}
              </span>
            </div>
            {log.note && (
              <p className="text-sm text-foreground/80">{log.note}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
