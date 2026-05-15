# File: routes/calls.py
# Purpose: GET /api/calls — returns paginated call log
# Step: Step-5

from flask import Blueprint, jsonify, request
from db.schema import get_connection


# --- Constants ---
DEFAULT_PAGE      = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE     = 100


calls_bp = Blueprint("calls", __name__)


def _fetch_calls(conn, page: int, page_size: int) -> dict:
    # WHY: Pagination prevents sending all rows to the frontend at once —
    # important once logs grow beyond a few hundred rows
    offset = (page - 1) * page_size
    rows = conn.execute("""
        SELECT id, model, prompt_tokens, completion_tokens,
               estimated_cost, actual_cost, urgency, status, timestamp
        FROM calls
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    """, (page_size, offset)).fetchall()

    total = conn.execute("SELECT COUNT(*) AS n FROM calls").fetchone()["n"]

    return {
        "page":       page,
        "page_size":  page_size,
        "total":      total,
        "calls":      [dict(r) for r in rows],
    }


@calls_bp.route("/api/calls", methods=["GET"])
def get_calls():
    # WHY: clamp page_size so callers can't request 10,000 rows in one shot
    page      = max(1, request.args.get("page", DEFAULT_PAGE, type=int))
    page_size = min(
        MAX_PAGE_SIZE,
        request.args.get("page_size", DEFAULT_PAGE_SIZE, type=int)
    )
    conn = get_connection()
    data = _fetch_calls(conn, page, page_size)
    conn.close()
    return jsonify(data), 200
