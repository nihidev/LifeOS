"use client"

import { useState } from "react"
import { Pencil, X, Check, Trash2 } from "lucide-react"
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
import { AIAnalysisCard, AIAnalysisCardSkeleton } from "./AIAnalysisCard"
import { useUpdateResolution, useDeleteResolution } from "@/hooks/useResolutions"
import type { AIAnalysisItem, ResolutionResponse, ResolutionStatus } from "@/types/resolution"

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
  analysisItem?: AIAnalysisItem
  analysisLoading?: boolean
  onClickMonth: (resolutionId: string, year: number, month: number) => void
}

export function ResolutionCard({
  resolution,
  analysisItem,
  analysisLoading,
  onClickMonth,
}: ResolutionCardProps) {
  const [editing, setEditing] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [title, setTitle] = useState(resolution.title)
  const [description, setDescription] = useState(resolution.description ?? "")
  const [status, setStatus] = useState<ResolutionStatus>(resolution.status)
  const [progress, setProgress] = useState(String(resolution.progress_percent))
  const [targetDate, setTargetDate] = useState(resolution.target_date ?? "")

  const { mutateAsync, isPending } = useUpdateResolution()
  const { mutateAsync: deleteResolution, isPending: isDeleting } = useDeleteResolution()

  async function handleSave() {
    try {
      await mutateAsync({
        id: resolution.id,
        body: {
          title: title.trim() || undefined,
          description: description.trim() || undefined,
          status,
          progress_percent: Number(progress),
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
    setProgress(String(resolution.progress_percent))
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
                <label className="text-xs text-muted-foreground">Progress %</label>
                <Input
                  type="number"
                  min={0}
                  max={100}
                  value={progress}
                  onChange={(e) => setProgress(e.target.value)}
                  className="h-8 w-20 text-sm"
                />
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
          <span className="text-xs text-muted-foreground w-8 text-right">
            {resolution.progress_percent}%
          </span>
        </div>

        {/* Month heatmap */}
        <MonthHeatmap
          checkIns={resolution.check_ins}
          onClickMonth={(year, month) => onClickMonth(resolution.id, year, month)}
        />

        {/* AI analysis */}
        {analysisLoading ? (
          <AIAnalysisCardSkeleton />
        ) : analysisItem ? (
          <AIAnalysisCard item={analysisItem} />
        ) : null}
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
    </Card>
  )
}
