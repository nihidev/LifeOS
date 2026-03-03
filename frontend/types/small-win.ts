export interface SmallWinResponse {
  id: string
  date: string
  text: string
  created_at: string
  updated_at: string
}

export interface SmallWinCreateInput {
  date: string
  text: string
}

export interface SmallWinUpdateInput {
  text: string
}
