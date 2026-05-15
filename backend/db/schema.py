# File: schema.py
# Purpose: Creates the SQLite `calls` table if it doesn't exist
# Step: Step-1

import sys, os
# WHY: sys.path insert lets us import constants from backend/
# without installing the project as a package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sqlite3
from constants import DB_PATH


def create_tables(conn: sqlite3.Connection) -> None:
    # WHY: Separation of table creation from connection logic
    # keeps each function doing exactly one thing
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            model             TEXT NOT NULL,
            prompt_tokens     INTEGER NOT NULL,
            completion_tokens INTEGER NOT NULL,
            estimated_cost    REAL NOT NULL,
            actual_cost       REAL NOT NULL,
            urgency           INTEGER NOT NULL,  -- 1 (low) to 5 (critical)
            status            TEXT NOT NULL,     -- success | error | rate_limited
            timestamp         TEXT NOT NULL      -- ISO-8601 string
        )
    """)
    conn.commit()


def create_circuit_breaker_table(conn: sqlite3.Connection) -> None:
    # WHY: Persisting state to SQLite means circuit breaker survives
    # Flask restarts — in-memory state alone would reset on every restart
    conn.execute("""
        CREATE TABLE IF NOT EXISTS circuit_breaker_state (
            provider     TEXT PRIMARY KEY,  -- e.g. "openai", "openrouter"
            state        TEXT NOT NULL,     -- CLOSED | OPEN | HALF_OPEN
            error_count  INTEGER DEFAULT 0,
            call_count   INTEGER DEFAULT 0,
            opened_at    TEXT,              -- ISO-8601, NULL when CLOSED
            updated_at   TEXT NOT NULL
        )
    """)
    conn.commit()


def get_connection() -> sqlite3.Connection:
    # WHY: Single entry point for DB connections so DB_PATH is
    # never scattered across files
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, not index
    return conn


if __name__ == "__main__":
    conn = get_connection()
    create_tables(conn)
    create_circuit_breaker_table(conn)
    print("✅ Tables created at", DB_PATH)

