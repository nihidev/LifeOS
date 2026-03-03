export interface SmallWinResponse {
  id: string
  date: string
  text: string
  entry_type: "win" | "task"
  completed: boolean | null
  created_at: string
  updated_at: string
}

export interface SmallWinCreateInput {
  date: string
  text: string
  entry_type?: "win" | "task"
}

export interface SmallWinUpdateInput {
  text?: string
  completed?: boolean
}
