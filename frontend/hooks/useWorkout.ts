"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type {
  MonthlySummaryResponse,
  StreakResponse,
  WorkoutCreateInput,
  WorkoutResponse,
} from "@/types/workout"

const KEY = "workouts"

export function useWorkout(date: string) {
  return useQuery<WorkoutResponse | null>({
    queryKey: [KEY, "day", date],
    queryFn: () => api.get<WorkoutResponse | null>(`/api/v1/workouts/?date=${date}`),
    enabled: !!date,
  })
}

export function useWorkoutStreak() {
  return useQuery<StreakResponse>({
    queryKey: [KEY, "streak"],
    queryFn: () => api.get<StreakResponse>("/api/v1/workouts/streak"),
  })
}

export function useWorkoutMonthlySummary(year: number, month: number) {
  return useQuery<MonthlySummaryResponse>({
    queryKey: [KEY, "monthly", year, month],
    queryFn: () =>
      api.get<MonthlySummaryResponse>(
        `/api/v1/workouts/monthly-summary?year=${year}&month=${month}`
      ),
  })
}

export function useLogWorkout() {
  const qc = useQueryClient()
  return useMutation<WorkoutResponse, Error, WorkoutCreateInput>({
    mutationFn: (body) => api.post<WorkoutResponse>("/api/v1/workouts/", body),
    onSuccess: (data) => {
      const d = new Date(data.date + "T00:00:00")
      qc.invalidateQueries({ queryKey: [KEY, "day", data.date] })
      qc.invalidateQueries({ queryKey: [KEY, "streak"] })
      qc.invalidateQueries({ queryKey: [KEY, "monthly", d.getFullYear(), d.getMonth() + 1] })
    },
  })
}
