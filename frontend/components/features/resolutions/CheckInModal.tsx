"use client"

import { useState } from "react"
import { Star } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useLogCheckIn } from "@/hooks/useResolutions"
import type { AIPlanMonth } from "@/types/resolution"

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
]

interface CheckInModalProps {
  resolutionId: string
  year: number
  month: number
  aiPlan: AIPlanMonth[] | null
  onClose: () => void
}

export function CheckInModal({ resolutionId, year, month, aiPlan, onClose }: CheckInModalProps) {
  const [rating, setRating] = useState(0)
  const [note, setNote] = useState("")
  const { mutateAsync, isPending } = useLogCheckIn()

  const monthLabel = `${MONTH_NAMES[month - 1]} ${year}`
  const planForMonth = aiPlan?.find((p) => p.month_label === monthLabel) ?? null

  async function handleSave() {
    if (rating === 0) return
    try {
      await mutateAsync({
        resolution_id: resolutionId,
        body: { year, month, rating, note: note.trim() || undefined },
      })
      onClose()
    } catch {
      // error handled by React Query
    }
  }

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>
            Log {MONTH_NAMES[month - 1]} {year} check-in
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-4 pt-2">
          {/* Plan context */}
          {planForMonth && (
            <div className="rounded-md bg-muted px-3 py-2 text-xs text-muted-foreground">
              <span className="mr-1">📋</span>
              <span className="font-medium">Plan for {monthLabel}:</span>{" "}
              &ldquo;{planForMonth.goal}&rdquo;
            </div>
          )}

          {/* Star rating */}
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((n) => (
              <button key={n} onClick={() => setRating(n)}>
                <Star
                  className={`w-7 h-7 transition-colors ${
                    n <= rating
                      ? "fill-yellow-400 text-yellow-400"
                      : "text-muted-foreground"
                  }`}
                />
              </button>
            ))}
          </div>

          {/* Note */}
          <Textarea
            placeholder="What did you accomplish this month?"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={4}
          />

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={onClose} disabled={isPending}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={rating === 0 || isPending}>
              Save
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
