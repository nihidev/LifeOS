export interface DashboardResponse {
  date: string
  integrity_score_today: number | null
  workout_streak: number
  did_workout_today: boolean
  monthly_expense_total: string
  active_resolutions: number
  completed_resolutions: number
  small_wins_today: number
  last_7_days_integrity: (number | null)[]
  expense_summary_this_month: Record<string, string>
}
