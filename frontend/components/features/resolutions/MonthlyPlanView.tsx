"use client"

import { useState } from "react"
import { ChevronDown, ChevronRight, Loader2, Sparkles, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import { useGeneratePlan } from "@/hooks/useResolutions"
import type { AIPlanMonth } from "@/types/resolution"

interface MonthlyPlanViewProps {
  resolutionId: string
  hasTargetDate: boolean
  plan: AIPlanMonth[] | null
}

export function MonthlyPlanView({ resolutionId, hasTargetDate, plan }: MonthlyPlanViewProps) {
  const [expanded, setExpanded] = useState(false)
  const { mutateAsync: generatePlan, isPending } = useGeneratePlan()

  if (!hasTargetDate && !plan) return null

  async function handleGenerate() {
    try {
      await generatePlan(resolutionId)
      setExpanded(true)
    } catch {
      toast.error("Failed to generate plan")
    }
  }

  if (isPending) {
    return (
      <div className="flex flex-col gap-2 pt-1">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-4/5" />
        <Skeleton className="h-3 w-3/5" />
      </div>
    )
  }

  if (!plan) {
    return (
      <Button
        variant="outline"
        size="sm"
        className="self-start gap-1.5 text-xs h-7"
        onClick={handleGenerate}
      >
        <Sparkles className="h-3 w-3" />
        Generate Plan
      </Button>
    )
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <button
          className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? (
            <ChevronDown className="h-3.5 w-3.5" />
          ) : (
            <ChevronRight className="h-3.5 w-3.5" />
          )}
          AI Monthly Plan ({plan.length} months)
        </button>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 px-1.5 text-xs text-muted-foreground"
          onClick={handleGenerate}
          disabled={isPending}
        >
          <RotateCcw className="h-3 w-3 mr-1" />
          Regenerate
        </Button>
      </div>

      {expanded && (
        <div className="flex flex-col gap-3 pl-4 pt-1 border-l border-border ml-1.5">
          {plan.map((month) => (
            <div key={month.month_label} className="flex flex-col gap-0.5">
              <p className="text-xs font-semibold">
                {month.month_label}{" "}
                <span className="font-normal text-muted-foreground">— {month.goal}</span>
              </p>
              <ul className="flex flex-col gap-0.5 pl-3">
                {month.actions.map((action, i) => (
                  <li key={i} className="text-xs text-muted-foreground list-disc">
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
