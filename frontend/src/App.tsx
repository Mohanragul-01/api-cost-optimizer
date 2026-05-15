// File: App.tsx
// Purpose: Root component — fetches shared data, composes all four panels
// Step: Step-7

import { useEffect, useState } from "react"
import type { StatsResponse, CircuitBreakerRow } from "./types/api"
import BudgetGauge           from "./components/BudgetGauge"
import CallLogTable          from "./components/CallLogTable"
import CircuitBreakerPanel   from "./components/CircuitBreakerPanel"
import AIRecommendations     from "./components/AIRecommendations"
import API_BASE from "./config"


const POLL_INTERVAL   = 30000  // WHY: refresh stats every 30s without user action


export default function App() {
  const [stats,    setStats]    = useState<StatsResponse | null>(null)
  const [breakers, setBreakers] = useState<CircuitBreakerRow[]>([])

  function fetchSharedData() {
    // WHY: stats + circuit breakers are fetched together — both used by multiple panels
    fetch(`${API_BASE}/api/stats`)
      .then(r => r.json()).then(setStats)

    fetch(`${API_BASE}/api/circuit-breakers`)
      .then(r => r.json()).then(setBreakers)
  }

  useEffect(() => {
    fetchSharedData()
    const id = setInterval(fetchSharedData, POLL_INTERVAL)
    return () => clearInterval(id)  // WHY: cleanup prevents memory leak on unmount
  }, [])

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-2xl font-bold mb-6 text-indigo-400">
        AI API Cost Optimizer
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <BudgetGauge            stats={stats} />
        <CircuitBreakerPanel    breakers={breakers} />
        <div className="md:col-span-2">
          <CallLogTable />
        </div>
        <div className="md:col-span-2">
          <AIRecommendations />
        </div>
      </div>
    </div>
  )
}
