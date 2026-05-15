// File: CallLogTable.tsx
// Purpose: Paginated table of recent LLM calls with cost, status, urgency
// Step: Step-7

import { useState, useEffect } from "react"
import type { CallsResponse, CallRow } from "../types/api"
import API_BASE from "../config"


// --- Constants ---
const PAGE_SIZE = 10


// WHY: Status colors defined as a map — avoids a chain of if/else in JSX
const STATUS_COLOR: Record<string, string> = {
  success:      "text-green-400",
  error:        "text-red-400",
  rate_limited: "text-yellow-400",
}


function CallRowItem({ call }: { call: CallRow }) {
  // WHY: Extracted to keep the table body clean and each row independently readable
  return (
    <tr className="border-t border-gray-700 hover:bg-gray-750">
      <td className="py-2 px-3 text-gray-300 text-sm">{call.model}</td>
      <td className="py-2 px-3 text-gray-300 text-sm">{call.prompt_tokens}</td>
      <td className="py-2 px-3 text-gray-300 text-sm">${call.actual_cost.toFixed(5)}</td>
      <td className="py-2 px-3 text-sm font-medium">
        <span className={STATUS_COLOR[call.status] ?? "text-gray-400"}>
          {call.status}
        </span>
      </td>
      <td className="py-2 px-3 text-gray-300 text-sm">{call.urgency}</td>
      <td className="py-2 px-3 text-gray-400 text-xs">
        {new Date(call.timestamp).toLocaleString()}
      </td>
    </tr>
  )
}


export default function CallLogTable() {
  const [data, setData]   = useState<CallsResponse | null>(null)
  const [page, setPage]   = useState(1)

  useEffect(() => {
    // WHY: Re-fetch whenever page changes — keeps data in sync with pagination
    fetch(`${API_BASE}/api/calls?page=${page}&page_size=${PAGE_SIZE}`)
      .then(r => r.json())
      .then(setData)
  }, [page])

  if (!data) return <div className="text-gray-400 text-sm">Loading calls…</div>

  const totalPages = Math.ceil(data.total / PAGE_SIZE)

  return (
    <div className="bg-gray-800 rounded-2xl p-6 shadow-lg">
      <h2 className="text-white text-lg font-semibold mb-4">
        Call Log <span className="text-gray-400 text-sm font-normal">({data.total} total)</span>
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="text-gray-400 text-xs uppercase">
              {["Model","Tokens","Cost","Status","Urgency","Time"].map(h => (
                <th key={h} className="py-2 px-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.calls.map(c => <CallRowItem key={c.id} call={c} />)}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center mt-4 text-sm">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-40"
        >← Prev</button>
        <span className="text-gray-400">Page {page} of {totalPages}</span>
        <button
          onClick={() => setPage(p => Math.min(totalPages, p + 1))}
          disabled={page === totalPages}
          className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-40"
        >Next →</button>
      </div>
    </div>
  )
}
