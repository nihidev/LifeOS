"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useAddResolution } from "@/hooks/useResolutions"

export function ResolutionForm() {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [targetDate, setTargetDate] = useState("")
  const { mutateAsync, isPending } = useAddResolution()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    try {
      await mutateAsync({
        title: title.trim(),
        description: description.trim() || undefined,
        target_date: targetDate || undefined,
      })
      setTitle("")
      setDescription("")
      setTargetDate("")
    } catch {
      // error handled by React Query
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <Input
        placeholder="Resolution title *"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <Textarea
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={2}
      />
      <div className="flex gap-2 items-end">
        <div className="flex flex-col gap-1 flex-1">
          <label className="text-xs text-muted-foreground">Target date (optional)</label>
          <Input
            type="date"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={isPending || !title.trim()} className="shrink-0">
          Add
        </Button>
      </div>
    </form>
  )
}
