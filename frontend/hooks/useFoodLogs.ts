"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type {
  FoodDailySummaryResponse,
  FoodLogCreateInput,
  FoodLogResponse,
  GenerateSummaryInput,
  WaterIntakeResponse,
} from "@/types/food-log"

const FOOD_KEY = "food-logs"
const WATER_KEY = "water-intake"
const SUMMARY_KEY = "food-daily-summary"

export function useFoodLogs(date: string) {
  return useQuery<FoodLogResponse[]>({
    queryKey: [FOOD_KEY, date],
    queryFn: () => api.get<FoodLogResponse[]>(`/api/v1/food-logs/?date=${date}`),
    enabled: !!date,
  })
}

export function useAddFoodLog() {
  const qc = useQueryClient()
  return useMutation<FoodLogResponse, Error, FoodLogCreateInput>({
    mutationFn: (body) => api.post<FoodLogResponse>("/api/v1/food-logs/", body),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: [FOOD_KEY, data.date] })
    },
  })
}

export function useDeleteFoodLog() {
  const qc = useQueryClient()
  return useMutation<{ message: string }, Error, { id: string; date: string }>({
    mutationFn: ({ id }) =>
      api.delete<{ message: string }>(`/api/v1/food-logs/${id}`),
    onSuccess: (_, { date }) => {
      qc.invalidateQueries({ queryKey: [FOOD_KEY, date] })
    },
  })
}

export function useWater(date: string) {
  return useQuery<WaterIntakeResponse>({
    queryKey: [WATER_KEY, date],
    queryFn: () =>
      api.get<WaterIntakeResponse>(`/api/v1/food-logs/water?date=${date}`),
    enabled: !!date,
  })
}

export function useWaterIncrement() {
  const qc = useQueryClient()
  return useMutation<WaterIntakeResponse, Error, { date: string }>({
    mutationFn: ({ date }) =>
      api.post<WaterIntakeResponse>("/api/v1/food-logs/water/increment", { date }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: [WATER_KEY, data.date] })
    },
  })
}

export function useWaterDecrement() {
  const qc = useQueryClient()
  return useMutation<WaterIntakeResponse, Error, { date: string }>({
    mutationFn: ({ date }) =>
      api.post<WaterIntakeResponse>("/api/v1/food-logs/water/decrement", { date }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: [WATER_KEY, data.date] })
    },
  })
}

export function useDailySummary(date: string) {
  return useQuery<FoodDailySummaryResponse | null>({
    queryKey: [SUMMARY_KEY, date],
    queryFn: async () => {
      try {
        return await api.get<FoodDailySummaryResponse>(
          `/api/v1/food-logs/summary?date=${date}`
        )
      } catch {
        return null
      }
    },
    enabled: !!date,
  })
}

export function useGenerateSummary() {
  const qc = useQueryClient()
  return useMutation<FoodDailySummaryResponse, Error, GenerateSummaryInput>({
    mutationFn: (body) =>
      api.post<FoodDailySummaryResponse>("/api/v1/food-logs/generate-summary", body),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: [SUMMARY_KEY, data.date] })
    },
  })
}
