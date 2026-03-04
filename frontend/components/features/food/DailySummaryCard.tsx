"use client"

import { Sparkles, RefreshCw } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useDailySummary, useGenerateSummary } from "@/hooks/useFoodLogs"

interface DailySummaryCardProps {
  date: string
  foodCount: number
}

function formatTime(isoString: string): string {
  return new Date(isoString).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  })
}

export function DailySummaryCard({ date, foodCount }: DailySummaryCardProps) {
  const { data: summary, isLoading } = useDailySummary(date)
  const generate = useGenerateSummary()

  if (foodCount === 0) return null

  async function handleGenerate() {
    try {
      await generate.mutateAsync({ date })
    } catch {
      toast.error("Failed to generate summary")
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            🥗 Daily Diet Summary
          </CardTitle>
          {summary && (
            <Button
              size="sm"
              variant="ghost"
              className="h-7 text-xs gap-1"
              onClick={handleGenerate}
              disabled={generate.isPending}
            >
              <RefreshCw className="h-3 w-3" />
              Regenerate
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex flex-col gap-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
          </div>
        ) : summary ? (
          <div className="flex flex-col gap-2">
            <p className="text-sm leading-relaxed">{summary.summary}</p>
            <p className="text-xs text-muted-foreground">
              Generated at {formatTime(summary.generated_at)}
            </p>
          </div>
        ) : (
          <Button
            variant="outline"
            className="w-full gap-2"
            onClick={handleGenerate}
            disabled={generate.isPending}
          >
            <Sparkles className="h-4 w-4" />
            {generate.isPending ? "Generating…" : "Generate AI Summary"}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
