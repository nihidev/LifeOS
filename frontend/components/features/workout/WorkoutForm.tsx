"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useLogWorkout } from "@/hooks/useWorkout"
import type { WorkoutResponse } from "@/types/workout"

interface WorkoutFormProps {
  date: string
  existing: WorkoutResponse | null
}

export function WorkoutForm({ date, existing }: WorkoutFormProps) {
  const [didWorkout, setDidWorkout] = useState<boolean | null>(
    existing ? existing.did_workout : null
  )
  const [activityType, setActivityType] = useState(existing?.activity_type ?? "")
  const [durationMins, setDurationMins] = useState(
    existing?.duration_mins?.toString() ?? ""
  )
  const [notes, setNotes] = useState(existing?.notes ?? "")
  const log = useLogWorkout()

  async function handleSubmit(workout: boolean) {
    setDidWorkout(workout)
    try {
      await log.mutateAsync({
        date,
        did_workout: workout,
        activity_type: activityType.trim() || undefined,
        duration_mins: durationMins ? parseInt(durationMins) : undefined,
        notes: notes.trim() || undefined,
      })
    } catch (err) {
      console.error("[WorkoutForm] submit failed:", err)
    }
  }

  const isToday = date === new Date().toISOString().slice(0, 10)

  return (
    <div className="flex flex-col gap-5">
      <div className="flex gap-3">
        <Button
          variant={didWorkout === true ? "default" : "outline"}
          className="flex-1 h-14 text-base"
          onClick={() => handleSubmit(true)}
          disabled={log.isPending}
        >
          ✅ Yes, I worked out
        </Button>
        <Button
          variant={didWorkout === false ? "destructive" : "outline"}
          className="flex-1 h-14 text-base"
          onClick={() => handleSubmit(false)}
          disabled={log.isPending}
        >
          🛌 Rest day
        </Button>
      </div>

      {didWorkout === true && (
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
          <Button
            onClick={() => handleSubmit(true)}
            disabled={log.isPending}
            className="self-end"
          >
            {log.isPending ? "Saving…" : existing ? "Update" : "Save"}
          </Button>
        </div>
      )}

      {log.isError && (
        <p className="text-sm text-destructive">{log.error.message}</p>
      )}

      {existing && (
        <p className="text-xs text-muted-foreground text-center">
          {isToday ? "Today's" : "This day's"} entry logged —{" "}
          {existing.did_workout ? "Workout ✅" : "Rest day 🛌"}
          {existing.activity_type ? ` · ${existing.activity_type}` : ""}
          {existing.duration_mins ? ` · ${existing.duration_mins} min` : ""}
        </p>
      )}
    </div>
  )
}
