export type ExpenseCategory =
  | "Groceries"
  | "Transport"
  | "Social Life"
  | "Fitness"
  | "Lifestyle"
  | "Bills"
  | "Self-improvement"

export const EXPENSE_CATEGORIES: ExpenseCategory[] = [
  "Groceries",
  "Transport",
  "Social Life",
  "Fitness",
  "Lifestyle",
  "Bills",
  "Self-improvement",
]

export interface ExpenseResponse {
  id: string
  date: string
  amount: number
  category: ExpenseCategory
  note: string | null
  created_at: string
  updated_at: string
}

export interface ExpenseCreateInput {
  date: string
  amount: number
  category: ExpenseCategory
  note?: string
}

export interface ExpenseUpdateInput {
  amount?: number
  category?: ExpenseCategory
  note?: string
}

export interface CategorySummary {
  category: string
  total: number
  count: number
}

export interface SummaryResponse {
  period: string
  total: number
  by_category: CategorySummary[]
}
