"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type {
  SmallWinCreateInput,
  SmallWinResponse,
  SmallWinStats,
  SmallWinUpdateInput,
} from "@/types/small-win"

const QUERY_KEY = "small-wins"
const STATS_KEY = "small-wins-stats"

export function useSmallWins(date: string) {
  return useQuery<SmallWinResponse[]>({
    queryKey: [QUERY_KEY, date],
    queryFn: () => api.get<SmallWinResponse[]>(`/api/v1/small-wins/?date=${date}`),
    enabled: !!date,
  })
}

export function useSmallWinStats() {
  return useQuery<SmallWinStats>({
    queryKey: [STATS_KEY],
    queryFn: () => api.get<SmallWinStats>("/api/v1/small-wins/stats"),
  })
}

export function useCreateSmallWin() {
  const qc = useQueryClient()
  return useMutation<SmallWinResponse, Error, SmallWinCreateInput>({
    mutationFn: (body) => api.post<SmallWinResponse>("/api/v1/small-wins/", body),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY, data.date] })
      qc.invalidateQueries({ queryKey: [STATS_KEY] })
    },
  })
}

export function useUpdateSmallWin() {
  const qc = useQueryClient()
  return useMutation<
    SmallWinResponse,
    Error,
    { id: string; date: string; body: SmallWinUpdateInput }
  >({
    mutationFn: ({ id, body }) =>
      api.patch<SmallWinResponse>(`/api/v1/small-wins/${id}`, body),
    onSuccess: (_, { date }) => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY, date] })
    },
  })
}

export function useToggleComplete() {
  const qc = useQueryClient()
  return useMutation<
    SmallWinResponse,
    Error,
    { id: string; date: string; completed: boolean }
  >({
    mutationFn: ({ id, completed }) =>
      api.patch<SmallWinResponse>(`/api/v1/small-wins/${id}`, { completed }),
    onSuccess: (_, { date }) => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY, date] })
      qc.invalidateQueries({ queryKey: [STATS_KEY] })
    },
  })
}

export function useDeleteSmallWin() {
  const qc = useQueryClient()
  return useMutation<{ message: string }, Error, { id: string; date: string }>({
    mutationFn: ({ id }) =>
      api.delete<{ message: string }>(`/api/v1/small-wins/${id}`),
    onSuccess: (_, { date }) => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY, date] })
    },
  })
}
