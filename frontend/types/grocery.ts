export interface GroceryItemResponse {
  id: string
  item: string
  quantity: string | null
  checked: boolean
  created_at: string
  updated_at: string
}

export interface GroceryItemCreateInput {
  item: string
  quantity?: string
}

export interface GroceryItemUpdateInput {
  item?: string
  quantity?: string
  checked?: boolean
}

export interface ClearCheckedResponse {
  deleted_count: number
}
