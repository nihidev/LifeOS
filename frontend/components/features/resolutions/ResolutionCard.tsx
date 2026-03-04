"use client"

import { useState } from "react"
import { Pencil, X, Check, Trash2, RefreshCw } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { MonthHeatmap } from "./MonthHeatmap"
import { MonthlyPlanView } from "./MonthlyPlanView"
import { LogProgressModal } from "./LogProgressModal"
import { ProgressHistory } from "./ProgressHistory"
import { useUpdateResolution, useDeleteResolution, useCalculateProgress } from "@/hooks/useResolutions"
import { toast } from "sonner"
import type { ResolutionResponse, ResolutionStatus } from "@/types/resolution"

function statusBadge(status: ResolutionStatus) {
  switch (status) {
    case "completed":
      return <Badge className="bg-green-500 text-white hover:bg-green-600">completed</Badge>
    case "in_progress":
      return <Badge className="bg-blue-500 text-white hover:bg-blue-600">in progress</Badge>
    default:
      return <Badge variant="secondary">not started</Badge>
  }
}

interface ResolutionCardProps {
  resolution: ResolutionResponse
  onClickMonth: (resolutionId: string, year: number, month: number) => void
}

export function ResolutionCard({
  resolution,
  onClickMonth,
}: ResolutionCardProps) {
  const [editing, setEditing] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [title, setTitle] = useState(resolution.title)
  const [description, setDescription] = useState(resolution.description ?? "")
  const [status, setStatus] = useState<ResolutionStatus>(resolution.status)
  const [targetDate, setTargetDate] = useState(resolution.target_date ?? "")
  const [loggingProgress, setLoggingProgress] = useState(false)

  const { mutateAsync, isPending } = useUpdateResolution()
  const { mutateAsync: deleteResolution, isPending: isDeleting } = useDeleteResolution()
  const { mutateAsync: calcProgress, isPending: isCalcPending } = useCalculateProgress()

  async function handleSave() {
    try {
      await mutateAsync({
        id: resolution.id,
        body: {
          title: title.trim() || undefined,
          description: description.trim() || undefined,
          status,
          target_date: targetDate || undefined,
        },
      })
      setEditing(false)
    } catch {
      // error visible via React Query
    }
  }

  function handleCancel() {
    setTitle(resolution.title)
    setDescription(resolution.description ?? "")
    setStatus(resolution.status)
    setTargetDate(resolution.target_date ?? "")
    setEditing(false)
  }


  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 flex-wrap">
            {editing ? (
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="h-7 text-sm font-semibold w-48"
              />
            ) : (
              <span className="font-semibold text-sm">{resolution.title}</span>
            )}
            {!editing && statusBadge(resolution.status)}
          </div>
          {editing ? (
            <div className="flex gap-1">
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={handleSave} disabled={isPending}>
                <Check className="h-3.5 w-3.5" />
              </Button>
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={handleCancel} disabled={isPending}>
                <X className="h-3.5 w-3.5" />
              </Button>
            </div>
          ) : (
            <div className="flex gap-1">
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => setEditing(true)}>
                <Pencil className="h-3.5 w-3.5" />
              </Button>
              <Button
                size="icon"
                variant="ghost"
                className="h-7 w-7 text-destructive hover:text-destructive"
                onClick={() => setConfirmDelete(true)}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>
          )}
        </div>

        {/* Edit fields */}
        {editing && (
          <div className="flex flex-col gap-2 mt-2">
            <Textarea
              placeholder="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="text-sm"
            />
            <div className="flex gap-2 flex-wrap">
              <div className="flex flex-col gap-1">
                <label className="text-xs text-muted-foreground">Status</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value as ResolutionStatus)}
                  className="h-8 rounded-md border border-input bg-background px-2 text-sm"
                >
                  <option value="not_started">not started</option>
                  <option value="in_progress">in progress</option>
                  <option value="completed">completed</option>
                </select>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs text-muted-foreground">Target date</label>
                <Input
                  type="date"
                  value={targetDate}
                  onChange={(e) => setTargetDate(e.target.value)}
                  className="h-8 text-sm"
                />
              </div>
            </div>
          </div>
        )}
      </CardHeader>

      <CardContent className="flex flex-col gap-3">
        {/* Progress bar */}
        <div className="flex items-center gap-2">
          <Progress value={resolution.progress_percent} className="flex-1 h-2" />
          <button
            className="text-xs text-muted-foreground w-8 text-right hover:text-foreground hover:underline transition-colors"
            title="Click to log progress"
            onClick={() => setLoggingProgress(true)}
          >
            {resolution.progress_percent}%
          </button>
          {resolution.ai_plan && (
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-muted-foreground"
              disabled={isCalcPending}
              onClick={async () => {
                try {
                  await calcProgress(resolution.id)
                } catch {
                  toast.error("Failed to recalculate progress")
                }
              }}
              title="AI recalculate"
            >
              <RefreshCw className={`h-3 w-3 ${isCalcPending ? "animate-spin" : ""}`} />
            </Button>
          )}
        </div>

        {/* Progress history */}
        <ProgressHistory logs={resolution.progress_logs} />

        {/* AI Monthly Plan */}
        <MonthlyPlanView
          resolutionId={resolution.id}
          hasTargetDate={!!resolution.target_date}
          plan={resolution.ai_plan}
        />

        {/* Month heatmap */}
        <MonthHeatmap
          checkIns={resolution.check_ins}
          onClickMonth={(year, month) => onClickMonth(resolution.id, year, month)}
        />

      </CardContent>

      <Dialog open={confirmDelete} onOpenChange={setConfirmDelete}>
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>Delete resolution?</DialogTitle>
            <DialogDescription>
              &ldquo;{resolution.title}&rdquo; and all its check-ins will be permanently deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmDelete(false)} disabled={isDeleting}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              disabled={isDeleting}
              onClick={async () => {
                try {
                  await deleteResolution(resolution.id)
                } catch {
                  setConfirmDelete(false)
                }
              }}
            >
              {isDeleting ? "Deleting…" : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {loggingProgress && (
        <LogProgressModal
          resolutionId={resolution.id}
          currentPercent={resolution.progress_percent}
          onClose={() => setLoggingProgress(false)}
        />
      )}
    </Card>
  )
}
