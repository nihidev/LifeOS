"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type {
  ExpenseCreateInput,
  ExpenseResponse,
  ExpenseUpdateInput,
  SummaryResponse,
} from "@/types/expense"

const KEY = "expenses"

const SUMMARY_KEYS = (qc: ReturnType<typeof useQueryClient>) => ({
  invalidateAll: (date: string) => {
    const [y, m] = date.split("-").map(Number)
    qc.invalidateQueries({ queryKey: [KEY, "day", date] })
    qc.invalidateQueries({ queryKey: [KEY, "weekly", date] })
    qc.invalidateQueries({ queryKey: [KEY, "monthly", y, m] })
    qc.invalidateQueries({ queryKey: [KEY, "cumulative"] })
    qc.invalidateQueries({ queryKey: [KEY, "all"] })
  },
})

export function useExpenses(date: string) {
  return useQuery<ExpenseResponse[]>({
    queryKey: [KEY, "day", date],
    queryFn: () => api.get<ExpenseResponse[]>(`/api/v1/expenses/?date=${date}`),
    enabled: !!date,
  })
}

export function useAllExpenses() {
  return useQuery<ExpenseResponse[]>({
    queryKey: [KEY, "all"],
    queryFn: () => api.get<ExpenseResponse[]>("/api/v1/expenses/all"),
  })
}

export function useWeeklySummary(date: string) {
  return useQuery<SummaryResponse>({
    queryKey: [KEY, "weekly", date],
    queryFn: () =>
      api.get<SummaryResponse>(`/api/v1/expenses/summary/weekly?date=${date}`),
    enabled: !!date,
  })
}

export function useMonthlySummary(year: number, month: number) {
  return useQuery<SummaryResponse>({
    queryKey: [KEY, "monthly", year, month],
    queryFn: () =>
      api.get<SummaryResponse>(
        `/api/v1/expenses/summary/monthly?year=${year}&month=${month}`
      ),
  })
}

export function useCumulativeSummary() {
  return useQuery<SummaryResponse>({
    queryKey: [KEY, "cumulative"],
    queryFn: () => api.get<SummaryResponse>("/api/v1/expenses/summary/cumulative"),
  })
}

export function useAddExpense() {
  const qc = useQueryClient()
  return useMutation<ExpenseResponse, Error, ExpenseCreateInput>({
    mutationFn: (body) => api.post<ExpenseResponse>("/api/v1/expenses/", body),
    onSuccess: (data) => {
      SUMMARY_KEYS(qc).invalidateAll(data.date)
    },
  })
}

export function useUpdateExpense() {
  const qc = useQueryClient()
  return useMutation<
    ExpenseResponse,
    Error,
    { id: string; date: string; body: ExpenseUpdateInput }
  >({
    mutationFn: ({ id, body }) =>
      api.patch<ExpenseResponse>(`/api/v1/expenses/${id}`, body),
    onSuccess: (_, { date }) => {
      SUMMARY_KEYS(qc).invalidateAll(date)
    },
  })
}

export function useDeleteExpense() {
  const qc = useQueryClient()
  return useMutation<{ message: string }, Error, { id: string; date: string }>({
    mutationFn: ({ id }) =>
      api.delete<{ message: string }>(`/api/v1/expenses/${id}`),
    onSuccess: (_, { date }) => {
      SUMMARY_KEYS(qc).invalidateAll(date)
    },
  })
}
