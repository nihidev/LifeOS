export type SmallWinCategory = "Work" | "Health" | "Personal Growth" | "General"

export interface SmallWinResponse {
  id: string
  date: string
  text: string
  entry_type: "win" | "task"
  completed: boolean | null
  category?: SmallWinCategory | null
  created_at: string
  updated_at: string
}

export interface SmallWinCreateInput {
  date: string
  text: string
  entry_type?: "win" | "task"
  category?: SmallWinCategory | null
}

export interface SmallWinUpdateInput {
  text?: string
  completed?: boolean
  category?: SmallWinCategory | null
}

export interface DayCount {
  date: string
  count: number
}

export interface SmallWinStats {
  total_wins: number
  wins_last_7_days: DayCount[]
}
