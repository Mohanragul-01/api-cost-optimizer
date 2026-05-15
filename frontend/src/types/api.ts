// File: types/api.ts
// Purpose: TypeScript interfaces matching every Flask API response shape
// Step: Step-7

export interface StatsResponse {
  mock_budget_usd:  number
  total_spend_usd:  number
  budget_remaining: number
  budget_used_pct:  number
  total_calls:      number
  success_count:    number
  error_count:      number
}


export interface CallRow {
  id:                 number
  model:              string
  prompt_tokens:      number
  completion_tokens:  number
  estimated_cost:     number
  actual_cost:        number
  urgency:            number
  status:             string
  timestamp:          string
}


export interface CallsResponse {
  page:      number
  page_size: number
  total:     number
  calls:     CallRow[]
}


export interface CircuitBreakerRow {
  provider:    string
  state:       "CLOSED" | "OPEN" | "HALF_OPEN"
  error_count: number
  call_count:  number
  opened_at:   string | null
  updated_at:  string | null
}


export interface Recommendation {
  title:                 string
  detail:                string
  estimated_saving_usd:  number
}


export interface AnalyzeResponse {
  summary:               string
  recommendations:       Recommendation[]
  projected_savings_usd: number
}
