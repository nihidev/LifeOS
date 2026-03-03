"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type {
  ClearCheckedResponse,
  GroceryItemCreateInput,
  GroceryItemResponse,
  GroceryItemUpdateInput,
} from "@/types/grocery"

const KEY = "grocery"

export function useGroceryItems() {
  return useQuery<GroceryItemResponse[]>({
    queryKey: [KEY],
    queryFn: () => api.get<GroceryItemResponse[]>("/api/v1/grocery/"),
  })
}

export function useAddGroceryItem() {
  const qc = useQueryClient()
  return useMutation<GroceryItemResponse, Error, GroceryItemCreateInput>({
    mutationFn: (body) => api.post<GroceryItemResponse>("/api/v1/grocery/", body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
    },
  })
}

export function useUpdateGroceryItem() {
  const qc = useQueryClient()
  return useMutation<
    GroceryItemResponse,
    Error,
    { id: string; body: GroceryItemUpdateInput }
  >({
    mutationFn: ({ id, body }) =>
      api.patch<GroceryItemResponse>(`/api/v1/grocery/${id}`, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
    },
  })
}

export function useDeleteGroceryItem() {
  const qc = useQueryClient()
  return useMutation<{ message: string }, Error, { id: string }>({
    mutationFn: ({ id }) =>
      api.delete<{ message: string }>(`/api/v1/grocery/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
    },
  })
}

export function useClearChecked() {
  const qc = useQueryClient()
  return useMutation<ClearCheckedResponse, Error, void>({
    mutationFn: () =>
      api.post<ClearCheckedResponse>("/api/v1/grocery/clear-checked"),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] })
    },
  })
}
