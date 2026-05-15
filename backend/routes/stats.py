# File: routes/stats.py
# Purpose: GET /api/stats — returns budget summary, total spend, call counts
# Step: Step-5

from flask import Blueprint, jsonify
from db.schema import get_connection


# --- Constants ---
MOCK_BUDGET_USD = 10.00  # WHY: hardcoded for MVP — Phase 2 makes this configurable


stats_bp = Blueprint("stats", __name__)


def _fetch_stats(conn) -> dict:
    # WHY: DB logic separated from route handler so it's unit-testable
    row = conn.execute("""
        SELECT
            COUNT(*)                          AS total_calls,
            SUM(actual_cost)                  AS total_spend,
            SUM(CASE WHEN status = 'error'
                THEN 1 ELSE 0 END)            AS error_count,
            SUM(CASE WHEN status = 'success'
                THEN 1 ELSE 0 END)            AS success_count
        FROM calls
    """).fetchone()

    total_spend = round(row["total_spend"] or 0.0, 6)

    return {
        "mock_budget_usd":    MOCK_BUDGET_USD,
        "total_spend_usd":    total_spend,
        "budget_remaining":   round(MOCK_BUDGET_USD - total_spend, 6),
        "budget_used_pct":    round((total_spend / MOCK_BUDGET_USD) * 100, 2),
        "total_calls":        row["total_calls"],
        "success_count":      row["success_count"],
        "error_count":        row["error_count"],
    }


@stats_bp.route("/api/stats", methods=["GET"])
def get_stats():
    conn = get_connection()
    data = _fetch_stats(conn)
    conn.close()
    return jsonify(data), 200
