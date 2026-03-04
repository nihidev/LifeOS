"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { ResolutionForm } from "@/components/features/resolutions/ResolutionForm"
import { ResolutionCard } from "@/components/features/resolutions/ResolutionCard"
import { CheckInModal } from "@/components/features/resolutions/CheckInModal"
import { useResolutions } from "@/hooks/useResolutions"
import type { ResolutionStatus } from "@/types/resolution"

type FilterValue = "all" | ResolutionStatus

const FILTERS: { label: string; value: FilterValue }[] = [
  { label: "All", value: "all" },
  { label: "In Progress", value: "in_progress" },
  { label: "Not Started", value: "not_started" },
  { label: "Completed", value: "completed" },
]

interface CheckInTarget {
  resolutionId: string
  year: number
  month: number
}

export default function ResolutionsPage() {
  const [filter, setFilter] = useState<FilterValue>("all")
  const [checkInTarget, setCheckInTarget] = useState<CheckInTarget | null>(null)

  const statusParam = filter === "all" ? undefined : filter
  const { data: resolutions = [], isLoading } = useResolutions(statusParam)

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        {/* Header */}
        <h1 className="text-2xl font-bold">Resolutions</h1>

        {/* Add form */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Add a Resolution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResolutionForm />
          </CardContent>
        </Card>

        {/* Filter strip */}
        <div className="flex gap-1 flex-wrap">
          {FILTERS.map(({ label, value }) => (
            <button
              key={value}
              onClick={() => setFilter(value)}
              className={`text-xs px-3 py-1 rounded-full font-medium transition-colors ${
                filter === value
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:text-foreground"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* List */}
        {isLoading ? (
          <div className="flex flex-col gap-4">
            {[1, 2].map((i) => (
              <div key={i} className="h-48 bg-muted animate-pulse rounded-xl" />
            ))}
          </div>
        ) : resolutions.length === 0 ? (
          <div className="text-center py-16 text-muted-foreground text-sm">
            No resolutions yet — add one above.
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {resolutions.map((r) => (
              <ResolutionCard
                key={r.id}
                resolution={r}
                onClickMonth={(resolutionId, year, month) =>
                  setCheckInTarget({ resolutionId, year, month })
                }
              />
            ))}
          </div>
        )}
      </div>

      {/* Check-in modal */}
      {checkInTarget && (
        <CheckInModal
          resolutionId={checkInTarget.resolutionId}
          year={checkInTarget.year}
          month={checkInTarget.month}
          aiPlan={resolutions.find((r) => r.id === checkInTarget.resolutionId)?.ai_plan ?? null}
          onClose={() => setCheckInTarget(null)}
        />
      )}
    </PageWrapper>
  )
}
