"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type {
  AIAnalysisResponse,
  CheckInCreateInput,
  ResolutionCreateInput,
  ResolutionResponse,
  ResolutionUpdateInput,
} from "@/types/resolution"

const KEY = "resolutions"

export function useResolutions(status?: string) {
  const params = status ? `?status_filter=${status}` : ""
  return useQuery<ResolutionResponse[]>({
    queryKey: [KEY, status ?? "all"],
    queryFn: () => api.get<ResolutionResponse[]>(`/api/v1/resolutions/${params}`),
  })
}

export function useAddResolution() {
  const qc = useQueryClient()
  return useMutation<ResolutionResponse, Error, ResolutionCreateInput>({
    mutationFn: (body) => api.post<ResolutionResponse>("/api/v1/resolutions/", body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
    },
  })
}

export function useUpdateResolution() {
  const qc = useQueryClient()
  return useMutation<
    ResolutionResponse,
    Error,
    { id: string; body: ResolutionUpdateInput }
  >({
    mutationFn: ({ id, body }) =>
      api.patch<ResolutionResponse>(`/api/v1/resolutions/${id}`, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
    },
  })
}

export function useLogCheckIn() {
  const qc = useQueryClient()
  return useMutation<
    ResolutionResponse,
    Error,
    { resolution_id: string; body: CheckInCreateInput }
  >({
    mutationFn: ({ resolution_id, body }) =>
      api.post<ResolutionResponse>(
        `/api/v1/resolutions/${resolution_id}/check-ins`,
        body
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
    },
  })
}

export function useDeleteResolution() {
  const qc = useQueryClient()
  return useMutation<void, Error, string>({
    mutationFn: (id) => api.delete(`/api/v1/resolutions/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
    },
  })
}

export function useAIAnalysis() {
  return useQuery<AIAnalysisResponse>({
    queryKey: [KEY, "analysis"],
    queryFn: () => api.get<AIAnalysisResponse>("/api/v1/resolutions/analysis"),
    staleTime: 60 * 60 * 1000, // 1 hour — backend caches daily
  })
}
