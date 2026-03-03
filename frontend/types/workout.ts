export interface WorkoutResponse {
  id: string
  date: string
  did_workout: boolean
  activity_type: string | null
  duration_mins: number | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface WorkoutCreateInput {
  date: string
  did_workout: boolean
  activity_type?: string
  duration_mins?: number
  notes?: string
}

export interface StreakResponse {
  current_streak: number
  longest_streak: number
}

export interface MonthlySummaryResponse {
  month: string
  total_days: number
  workout_days: number
  rest_days: number
  completion_percent: number
  entries: WorkoutResponse[]
}
