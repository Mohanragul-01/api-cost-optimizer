// File: BudgetGauge.tsx
// Purpose: Displays mock budget vs actual spend as a progress bar gauge
// Step: Step-7

import type { StatsResponse } from "../types/api"


// WHY: Props typed explicitly so TypeScript catches mismatched data at compile time
interface Props { stats: StatsResponse | null }


export default function BudgetGauge({ stats }: Props) {
  if (!stats) return <div className="text-gray-400 text-sm">Loading stats…</div>

  // WHY: Clamp to 100 so bar never overflows its container
  const pct = Math.min(stats.budget_used_pct, 100)

  // WHY: Color shifts to warn user as spend approaches budget
  const barColor =
    pct > 80 ? "bg-red-500" :
    pct > 50 ? "bg-yellow-400" :
               "bg-green-500"

  return (
    <div className="bg-gray-800 rounded-2xl p-6 shadow-lg">
      <h2 className="text-white text-lg font-semibold mb-4">Budget Usage</h2>

      <div className="flex justify-between text-sm text-gray-400 mb-1">
        <span>Spent: ${stats.total_spend_usd.toFixed(4)}</span>
        <span>Budget: ${stats.mock_budget_usd.toFixed(2)}</span>
      </div>

      {/* Track */}
      <div className="w-full bg-gray-700 rounded-full h-4">
        <div
          className={`${barColor} h-4 rounded-full transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>

      <p className="text-gray-400 text-sm mt-2">{pct.toFixed(1)}% used</p>

      <div className="grid grid-cols-3 gap-4 mt-4 text-center">
        {[
          { label: "Total Calls",  value: stats.total_calls },
          { label: "Successes",    value: stats.success_count },
          { label: "Errors",       value: stats.error_count },
        ].map(({ label, value }) => (
          <div key={label} className="bg-gray-700 rounded-xl p-3">
            <p className="text-white font-bold text-xl">{value}</p>
            <p className="text-gray-400 text-xs mt-1">{label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
