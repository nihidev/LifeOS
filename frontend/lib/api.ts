import { supabase } from "@/lib/auth"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export class ApiError extends Error {
  constructor(
    public message: string,
    public status: number
  ) {
    super(message)
    this.name = "ApiError"
  }
}

async function getAuthHeader(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const authHeaders = await getAuthHeader()
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...authHeaders,
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const data = await res.json()
      message = data?.detail ?? data?.message ?? message
    } catch {
      // ignore parse errors
    }
    console.error(`[api] ${method} ${path} → ${res.status}: ${message}`)
    throw new ApiError(message, res.status)
  }

  if (res.status === 204) {
    return undefined as T
  }

  return res.json() as Promise<T>
}

export const api = {
  get<T>(path: string): Promise<T> {
    return request<T>("GET", path)
  },
  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>("POST", path, body)
  },
  patch<T>(path: string, body?: unknown): Promise<T> {
    return request<T>("PATCH", path, body)
  },
  delete<T>(path: string): Promise<T> {
    return request<T>("DELETE", path)
  },
}
