// File: CircuitBreakerPanel.tsx
// Purpose: Shows green/yellow/red status indicator per provider
// Step: Step-7

import type { CircuitBreakerRow } from "../types/api"


interface Props { breakers: CircuitBreakerRow[] }


// WHY: State → color/label map keeps rendering logic out of JSX
const STATE_STYLE: Record<string, { dot: string; label: string }> = {
  CLOSED:    { dot: "bg-green-500",  label: "Closed"     },
  OPEN:      { dot: "bg-red-500",    label: "Open"       },
  HALF_OPEN: { dot: "bg-yellow-400", label: "Half-Open"  },
}


function BreakerCard({ b }: { b: CircuitBreakerRow }) {
  const style = STATE_STYLE[b.state] ?? { dot: "bg-gray-500", label: b.state }
  return (
    <div className="bg-gray-700 rounded-xl p-4 flex items-center gap-4">
      {/* WHY: animate-pulse makes OPEN state visually alarming at a glance */}
      <div className={`w-4 h-4 rounded-full ${style.dot} ${b.state === "OPEN" ? "animate-pulse" : ""}`} />
      <div>
        <p className="text-white font-medium capitalize">{b.provider}</p>
        <p className="text-gray-400 text-xs">
          {style.label} · {b.error_count} errors / {b.call_count} calls
        </p>
      </div>
    </div>
  )
}


export default function CircuitBreakerPanel({ breakers }: Props) {
  if (!breakers.length) return <div className="text-gray-400 text-sm">Loading…</div>
  return (
    <div className="bg-gray-800 rounded-2xl p-6 shadow-lg">
      <h2 className="text-white text-lg font-semibold mb-4">Circuit Breakers</h2>
      <div className="flex flex-col gap-3">
        {breakers.map(b => <BreakerCard key={b.provider} b={b} />)}
      </div>
    </div>
  )
}
