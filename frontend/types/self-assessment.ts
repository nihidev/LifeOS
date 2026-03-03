export interface SelfAssessmentResponse {
  id: string
  date: string
  performed_well_partner: boolean
  note: string | null
  integrity_score: number
  created_at: string
  updated_at: string
}

export interface SelfAssessmentHistoryResponse {
  entries: SelfAssessmentResponse[]
  average_score: number
}

export interface SelfAssessmentCreateInput {
  date: string
  performed_well_partner: boolean
  note?: string
}
