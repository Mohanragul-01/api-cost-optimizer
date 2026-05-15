# File: routes/circuit_breakers.py
# Purpose: GET /api/circuit-breakers — returns state for all known providers
# Step: Step-5

from flask import Blueprint, jsonify
from db.schema import get_connection
from circuit_breaker import CircuitBreaker


# --- Constants ---
# WHY: Defined here so adding a new provider means one line change
KNOWN_PROVIDERS = ["openai", "openrouter", "llama"]


circuit_breakers_bp = Blueprint("circuit_breakers", __name__)


def _fetch_all_states(conn) -> list:
    # WHY: Read persisted state directly from DB — no need to instantiate
    # a CircuitBreaker object just to read state
    rows = conn.execute(
        "SELECT provider, state, error_count, call_count, opened_at, updated_at "
        "FROM circuit_breaker_state"
    ).fetchall()
    persisted = {r["provider"]: dict(r) for r in rows}

    # WHY: Always return all known providers even if they have no DB row yet
    result = []
    for provider in KNOWN_PROVIDERS:
        if provider in persisted:
            result.append(persisted[provider])
        else:
            result.append({
                "provider":    provider,
                "state":       "CLOSED",
                "error_count": 0,
                "call_count":  0,
                "opened_at":   None,
                "updated_at":  None,
            })
    return result


@circuit_breakers_bp.route("/api/circuit-breakers", methods=["GET"])
def get_circuit_breakers():
    conn = get_connection()
    data = _fetch_all_states(conn)
    conn.close()
    return jsonify(data), 200
