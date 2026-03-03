"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type {
  SmallWinCreateInput,
  SmallWinResponse,
  SmallWinUpdateInput,
} from "@/types/small-win"

const QUERY_KEY = "small-wins"

export function useSmallWins(date: string) {
  return useQuery<SmallWinResponse[]>({
    queryKey: [QUERY_KEY, date],
    queryFn: () => api.get<SmallWinResponse[]>(`/api/v1/small-wins/?date=${date}`),
    enabled: !!date,
  })
}

export function useCreateSmallWin() {
  const qc = useQueryClient()
  return useMutation<SmallWinResponse, Error, SmallWinCreateInput>({
    mutationFn: (body) => api.post<SmallWinResponse>("/api/v1/small-wins/", body),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY, data.date] })
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
