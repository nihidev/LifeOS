"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type {
  SelfAssessmentCreateInput,
  SelfAssessmentHistoryResponse,
  SelfAssessmentResponse,
} from "@/types/self-assessment"

const KEY = "self-assessment"

export function useSelfAssessment(date: string) {
  return useQuery<SelfAssessmentResponse | null>({
    queryKey: [KEY, "day", date],
    queryFn: () =>
      api.get<SelfAssessmentResponse | null>(`/api/v1/self-assessment/?date=${date}`),
    enabled: !!date,
  })
}

export function useSelfAssessmentHistory(limit = 30, offset = 0) {
  return useQuery<SelfAssessmentHistoryResponse>({
    queryKey: [KEY, "history", limit, offset],
    queryFn: () =>
      api.get<SelfAssessmentHistoryResponse>(
        `/api/v1/self-assessment/history?limit=${limit}&offset=${offset}`
      ),
  })
}

export function useSaveAssessment() {
  const qc = useQueryClient()
  return useMutation<SelfAssessmentResponse, Error, SelfAssessmentCreateInput>({
    mutationFn: (body) =>
      api.post<SelfAssessmentResponse>("/api/v1/self-assessment/", body),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: [KEY, "day", data.date] })
      qc.invalidateQueries({ queryKey: [KEY, "history"] })
    },
  })
}
