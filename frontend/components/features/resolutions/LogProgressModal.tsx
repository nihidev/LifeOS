"use client"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Progress } from "@/components/ui/progress"
import { toast } from "sonner"
import { useLogProgress } from "@/hooks/useResolutions"

interface LogProgressModalProps {
  resolutionId: string
  currentPercent: number
  onClose: () => void
}

export function LogProgressModal({ resolutionId, currentPercent, onClose }: LogProgressModalProps) {
  const [percent, setPercent] = useState(String(currentPercent))
  const [note, setNote] = useState("")
  const { mutateAsync, isPending } = useLogProgress()

  const numericPercent = Math.max(0, Math.min(100, parseInt(percent, 10) || 0))

  async function handleSave() {
    const value = parseInt(percent, 10)
    if (isNaN(value) || value < 0 || value > 100) return
    try {
      await mutateAsync({ id: resolutionId, progress_percent: value, note: note.trim() || undefined })
      onClose()
    } catch {
      toast.error("Failed to log progress")
    }
  }

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>Log Progress</DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-4 pt-1">
          {/* Percentage input + live bar */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-3">
              <Input
                type="number"
                min={0}
                max={100}
                value={percent}
                onChange={(e) => setPercent(e.target.value)}
                className="w-20 text-center text-sm h-8"
                autoFocus
              />
              <span className="text-sm text-muted-foreground">% complete</span>
            </div>
            <Progress value={numericPercent} className="h-2" />
          </div>

          {/* Note */}
          <Textarea
            placeholder="What did you accomplish? (optional)"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={3}
          />

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={onClose} disabled={isPending}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isPending || isNaN(parseInt(percent, 10))}>
              {isPending ? "Saving…" : "Save"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
