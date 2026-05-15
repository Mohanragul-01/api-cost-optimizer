// File: AIRecommendations.tsx
// Purpose: Triggers /api/analyze and displays AI routing suggestions + savings
// Step: Step-7

import { useState } from "react"
import type { AnalyzeResponse, Recommendation } from "../types/api"
import API_BASE from "../config"


function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <div className="bg-gray-700 rounded-xl p-4">
      <p className="text-white font-medium">{rec.title}</p>
      <p className="text-gray-400 text-sm mt-1">{rec.detail}</p>
      <p className="text-green-400 text-sm mt-2 font-mono">
        Est. saving: ${rec.estimated_saving_usd.toFixed(4)}
      </p>
    </div>
  )
}


export default function AIRecommendations() {
  const [result,  setResult]  = useState<AnalyzeResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState<string | null>(null)

  async function runAnalysis() {
    // WHY: Reset error on each new attempt so stale errors don't persist
    setLoading(true)
    setError(null)
    try {
      const res  = await fetch(`${API_BASE}/api/analyze`, { method: "POST" })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? "Unknown error")
      setResult(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Request failed")
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="bg-gray-800 rounded-2xl p-6 shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-white text-lg font-semibold">AI Recommendations</h2>
        <button
          onClick={runAnalysis}
          disabled={loading}
          className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm
                     rounded-lg disabled:opacity-50 transition-colors"
        >
          {loading ? "Analyzing…" : "Run Analysis"}
        </button>
      </div>

      {error && <p className="text-red-400 text-sm mb-3">{error}</p>}

      {result && (
        <div className="flex flex-col gap-3">
          <p className="text-gray-300 text-sm italic">{result.summary}</p>
          {result.recommendations.map((r, i) => (
            <RecommendationCard key={i} rec={r} />
          ))}
          <p className="text-green-400 font-mono text-sm mt-1">
            Total projected saving: ${result.projected_savings_usd.toFixed(4)}
          </p>
        </div>
      )}

      {!result && !loading && (
        <p className="text-gray-500 text-sm">
          Click "Run Analysis" to get routing recommendations.
        </p>
      )}
    </div>
  )
}
