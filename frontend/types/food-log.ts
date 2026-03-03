export interface FoodLogResponse {
  id: string
  date: string
  consumed_at: string
  food_item: string
  ai_comment: string | null
  created_at: string
}

export interface FoodLogCreateInput {
  date: string
  consumed_at: string
  food_item: string
}

export interface WaterIntakeResponse {
  date: string
  glasses: number
}
