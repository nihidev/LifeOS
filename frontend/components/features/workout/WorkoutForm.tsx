"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useLogWorkout } from "@/hooks/useWorkout"

interface WorkoutFormProps {
  date: string
}

export function WorkoutForm({ date }: WorkoutFormProps) {
  const [showForm, setShowForm] = useState(false)
  const [activityType, setActivityType] = useState("")
  const [durationMins, setDurationMins] = useState("")
  const [notes, setNotes] = useState("")
  const log = useLogWorkout()

  async function handleRestDay() {
    try {
      await log.mutateAsync({ date, did_workout: false })
      setShowForm(false)
    } catch (err) {
      console.error("[WorkoutForm] submit failed:", err)
    }
  }

  async function handleSaveWorkout() {
    try {
      await log.mutateAsync({
        date,
        did_workout: true,
        activity_type: activityType.trim() || undefined,
        duration_mins: durationMins ? parseInt(durationMins) : undefined,
        notes: notes.trim() || undefined,
      })
      setShowForm(false)
      setActivityType("")
      setDurationMins("")
      setNotes("")
    } catch (err) {
      console.error("[WorkoutForm] submit failed:", err)
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex gap-3">
        <Button
          variant={showForm ? "default" : "outline"}
          className="flex-1 h-14 text-base"
          onClick={() => setShowForm((v) => !v)}
          disabled={log.isPending}
        >
          ✅ Yes, I worked out
        </Button>
        <Button
          variant="outline"
          className="flex-1 h-14 text-base"
          onClick={handleRestDay}
          disabled={log.isPending}
        >
          {log.isPending && !showForm ? "Saving…" : "🛌 Rest day"}
        </Button>
      </div>

      {showForm && (
        <div className="flex flex-col gap-4 p-4 rounded-lg border bg-muted/30">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="activity">Activity type</Label>
              <Input
                id="activity"
                placeholder="Running, Gym, Yoga…"
                value={activityType}
                onChange={(e) => setActivityType(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="duration">Duration (mins)</Label>
              <Input
                id="duration"
                type="number"
                placeholder="30"
                min={1}
                value={durationMins}
                onChange={(e) => setDurationMins(e.target.value)}
              />
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              placeholder="How did it feel?"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
            />
          </div>
          <div className="flex gap-2 self-end">
            <Button
              variant="ghost"
              onClick={() => setShowForm(false)}
              disabled={log.isPending}
            >
              Cancel
            </Button>
            <Button onClick={handleSaveWorkout} disabled={log.isPending}>
              {log.isPending ? "Saving…" : "Save"}
            </Button>
          </div>
        </div>
      )}

      {log.isError && (
        <p className="text-sm text-destructive">{log.error.message}</p>
      )}
    </div>
  )
}
