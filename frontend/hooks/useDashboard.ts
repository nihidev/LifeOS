"use client"

import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type { DashboardResponse } from "@/types/dashboard"

export function useDashboard() {
  return useQuery<DashboardResponse>({
    queryKey: ["dashboard"],
    queryFn: () => api.get<DashboardResponse>("/api/v1/dashboard/"),
    staleTime: 60 * 1000, // 1 minute
  })
}
