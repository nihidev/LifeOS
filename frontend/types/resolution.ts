export type ResolutionStatus = "not_started" | "in_progress" | "completed"
export type AISignal = "on_track" | "at_risk" | "no_signal"

export interface AIPlanMonth {
  month_label: string
  goal: string
  actions: string[]
}

export interface ProgressLogResponse {
  id: string
  progress_percent: number
  note: string | null
  logged_at: string
}

export interface CheckInResponse {
  id: string
  resolution_id: string
  year: number
  month: number
  rating: number
  note: string | null
  created_at: string
  updated_at: string
}

export interface ResolutionResponse {
  id: string
  title: string
  description: string | null
  status: ResolutionStatus
  progress_percent: number
  target_date: string | null
  ai_plan: AIPlanMonth[] | null
  created_at: string
  updated_at: string
  check_ins: CheckInResponse[]
  progress_logs: ProgressLogResponse[]
}

export interface CheckInCreateInput {
  year: number
  month: number
  rating: number
  note?: string
}

export interface ResolutionCreateInput {
  title: string
  description?: string
  target_date?: string
}

export interface ResolutionUpdateInput {
  title?: string
  description?: string
  status?: ResolutionStatus
  progress_percent?: number
  target_date?: string
}

export interface AIAnalysisItem {
  resolution_id: string
  resolution_title: string
  signal: AISignal
  evidence: string[]
  suggestion: string
}

export interface AIAnalysisResponse {
  generated_at: string
  analyses: AIAnalysisItem[]
}
