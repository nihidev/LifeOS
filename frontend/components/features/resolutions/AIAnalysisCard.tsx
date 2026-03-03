"use client"

import { Badge } from "@/components/ui/badge"
import type { AIAnalysisItem, AISignal } from "@/types/resolution"

function signalBadge(signal: AISignal) {
  switch (signal) {
    case "on_track":
      return <Badge className="bg-green-500 text-white hover:bg-green-600">on track</Badge>
    case "at_risk":
      return <Badge className="bg-amber-500 text-white hover:bg-amber-600">at risk</Badge>
    default:
      return <Badge variant="secondary">no signal</Badge>
  }
}

interface AIAnalysisCardProps {
  item: AIAnalysisItem
}

export function AIAnalysisCard({ item }: AIAnalysisCardProps) {
  return (
    <div className="flex flex-col gap-1 pt-2 border-t mt-2">
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-muted-foreground">AI signal</span>
        {signalBadge(item.signal)}
      </div>
      {item.signal !== "no_signal" && item.evidence.length > 0 && (
        <ul className="text-xs text-muted-foreground list-disc list-inside space-y-0.5">
          {item.evidence.slice(0, 3).map((ev, i) => (
            <li key={i}>{ev}</li>
          ))}
        </ul>
      )}
      {item.suggestion && (
        <p className="text-xs italic text-muted-foreground">{item.suggestion}</p>
      )}
    </div>
  )
}

export function AIAnalysisCardSkeleton() {
  return (
    <div className="flex flex-col gap-1 pt-2 border-t mt-2 animate-pulse">
      <div className="flex items-center gap-2">
        <div className="h-3 w-14 bg-muted rounded" />
        <div className="h-5 w-16 bg-muted rounded-full" />
      </div>
      <div className="h-3 w-full bg-muted rounded" />
    </div>
  )
}
