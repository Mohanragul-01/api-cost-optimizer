# File: circuit_breaker.py
# Purpose: Blocks calls to a provider when error rate exceeds threshold,
#          recovers automatically after a cooldown window
# Step: Step-4

import threading
from datetime import datetime, timedelta
from db.schema import get_connection, create_circuit_breaker_table


# --- Constants ---
ERROR_RATE_THRESHOLD = 0.50   # trip breaker if errors exceed 50% of calls
WINDOW_SECONDS       = 60     # sliding window for error rate calculation
RECOVERY_SECONDS     = 30     # how long to stay OPEN before trying HALF_OPEN
HALF_OPEN_TEST_CALLS = 1      # calls allowed through in HALF_OPEN to test recovery


# --- States ---
CLOSED    = "CLOSED"      # normal operation
OPEN      = "OPEN"        # all calls blocked
HALF_OPEN = "HALF_OPEN"   # one test call allowed through


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _load_state(conn, provider: str) -> dict:
    # WHY: Always read from DB so state is consistent across threads/restarts
    row = conn.execute(
        "SELECT * FROM circuit_breaker_state WHERE provider = ?", (provider,)
    ).fetchone()
    if row is None:
        return {"provider": provider, "state": CLOSED,
                "error_count": 0, "call_count": 0,
                "opened_at": None, "updated_at": _now_iso()}
    return dict(row)


def _save_state(conn, s: dict) -> None:
    # WHY: UPSERT pattern — inserts first time, updates every time after
    conn.execute("""
        INSERT INTO circuit_breaker_state
            (provider, state, error_count, call_count, opened_at, updated_at)
        VALUES (:provider, :state, :error_count, :call_count, :opened_at, :updated_at)
        ON CONFLICT(provider) DO UPDATE SET
            state       = excluded.state,
            error_count = excluded.error_count,
            call_count  = excluded.call_count,
            opened_at   = excluded.opened_at,
            updated_at  = excluded.updated_at
    """, s)
    conn.commit()


def _error_rate(s: dict) -> float:
    # WHY: Avoid division-by-zero on first call
    if s["call_count"] == 0:
        return 0.0
    return s["error_count"] / s["call_count"]


class CircuitBreaker:
    # WHY: One instance per provider — tracks that provider's health independently

    def __init__(self, provider: str) -> None:
        self.provider = provider
        self._lock = threading.Lock()
        conn = get_connection()
        create_circuit_breaker_table(conn)  # safe — uses IF NOT EXISTS
        conn.close()


    def get_state(self) -> str:
        with self._lock:
            conn = get_connection()
            s = _load_state(conn, self.provider)
            state = self._maybe_transition(conn, s)
            conn.close()
        return state


    def record_call(self, success: bool) -> None:
        # WHY: Every call outcome updates the window counters,
        # then we check if a transition is needed
        with self._lock:
            conn = get_connection()
            s = _load_state(conn, self.provider)
            s["call_count"]  += 1
            s["error_count"] += 0 if success else 1
            s["updated_at"]   = _now_iso()
            self._maybe_transition(conn, s)
            _save_state(conn, s)
            conn.close()


    def _maybe_transition(self, conn, s: dict) -> str:
        # WHY: All transition logic in one place — easier to test each branch
        if s["state"] == CLOSED and _error_rate(s) > ERROR_RATE_THRESHOLD:
            s["state"]     = OPEN
            s["opened_at"] = _now_iso()

        elif s["state"] == OPEN and s["opened_at"]:
            elapsed = (datetime.utcnow() - datetime.fromisoformat(s["opened_at"])).seconds
            if elapsed >= RECOVERY_SECONDS:
                s["state"]      = HALF_OPEN
                s["error_count"] = 0
                s["call_count"]  = 0

        elif s["state"] == HALF_OPEN and s["call_count"] >= HALF_OPEN_TEST_CALLS:
            s["state"] = CLOSED if _error_rate(s) == 0.0 else OPEN

        _save_state(conn, s)
        return s["state"]


    def is_open(self) -> bool:
        # WHY: Simple boolean for callers that just need to know "block or not"
        return self.get_state() == OPEN
