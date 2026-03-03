"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useSaveAssessment } from "@/hooks/useSelfAssessment"
import type { SelfAssessmentResponse } from "@/types/self-assessment"
import { toast } from "sonner"
import { cn } from "@/lib/utils"

interface Props {
  date: string
  existing: SelfAssessmentResponse | null
}

export function AssessmentForm({ date, existing }: Props) {
  const [selected, setSelected] = useState<boolean | null>(
    existing ? existing.performed_well_partner : null
  )
  const [note, setNote] = useState(existing?.note ?? "")
  const { mutateAsync, isPending } = useSaveAssessment()

  // Sync when date or existing changes
  useEffect(() => {
    setSelected(existing ? existing.performed_well_partner : null)
    setNote(existing?.note ?? "")
  }, [date, existing])

  async function handleSubmit() {
    if (selected === null) return
    try {
      await mutateAsync({
        date,
        performed_well_partner: selected,
        note: note.trim() || undefined,
      })
      toast.success("Assessment saved")
    } catch {
      toast.error("Failed to save assessment")
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm font-medium">Did you perform well as a partner today?</p>
      <div className="flex gap-3">
        <button
          type="button"
          onClick={() => setSelected(true)}
          className={cn(
            "flex-1 rounded-lg border-2 py-3 text-sm font-semibold transition-colors",
            selected === true
              ? "border-green-500 bg-green-50 text-green-700"
              : "border-border text-muted-foreground hover:border-green-300"
          )}
        >
          Yes
        </button>
        <button
          type="button"
          onClick={() => setSelected(false)}
          className={cn(
            "flex-1 rounded-lg border-2 py-3 text-sm font-semibold transition-colors",
            selected === false
              ? "border-red-500 bg-red-50 text-red-700"
              : "border-border text-muted-foreground hover:border-red-300"
          )}
        >
          No
        </button>
      </div>

      <Textarea
        placeholder={selected === false ? "Required — explain what went wrong" : "Optional note..."}
        value={note}
        onChange={(e) => setNote(e.target.value)}
        rows={2}
        className="resize-none"
      />

      {selected === false && note.trim() === "" && (
        <p className="text-xs text-destructive">A note is required when selecting No</p>
      )}

      <Button
        onClick={handleSubmit}
        disabled={
          selected === null ||
          isPending ||
          (selected === false && note.trim() === "")
        }
      >
        {isPending ? "Saving…" : "Save"}
      </Button>
    </div>
  )
}
