# File: seed.py
# Purpose: Populates the calls table with realistic mock data for dev/demo use
# Step: Step-1

import sys, os
import random
import sqlite3
from faker import Faker
from datetime import datetime, timedelta

# WHY: sys.path insert lets us import constants from backend/
# without installing the project as a package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from constants import DB_PATH, MODEL_PRICING, SEED_ROW_COUNT, URGENCY_LEVELS, CALL_STATUSES
from db.schema import get_connection, create_tables

fake = Faker()


def random_timestamp(days_back: int = 7) -> str:
    # WHY: Spreads mock data across the past week so charts look realistic
    delta = timedelta(seconds=random.randint(0, days_back * 86400))
    return (datetime.utcnow() - delta).isoformat()


def build_mock_row(model: str) -> tuple:
    # WHY: One function = one row; easy to test and reason about
    pricing = MODEL_PRICING[model]
    prompt_tokens = random.randint(50, 800)
    completion_tokens = random.randint(20, 400)

    estimated_cost = (
        (prompt_tokens / 1000) * pricing["input"] +
        (completion_tokens / 1000) * pricing["output"]
    )
    # WHY: actual_cost adds ±10% noise — real APIs never match estimates exactly
    actual_cost = round(estimated_cost * random.uniform(0.9, 1.1), 6)

    return (
        model,
        prompt_tokens,
        completion_tokens,
        round(estimated_cost, 6),
        actual_cost,
        random.choice(URGENCY_LEVELS),
        random.choice(CALL_STATUSES),
        random_timestamp(),
    )


def seed(conn: sqlite3.Connection, count: int = SEED_ROW_COUNT) -> None:
    models = list(MODEL_PRICING.keys())
    rows = [build_mock_row(random.choice(models)) for _ in range(count)]

    conn.executemany("""
        INSERT INTO calls
            (model, prompt_tokens, completion_tokens, estimated_cost,
             actual_cost, urgency, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    print(f"✅ Seeded {count} rows into {DB_PATH}")


def seed_if_empty(conn: sqlite3.Connection) -> None:
    existing = conn.execute(
        "SELECT COUNT(*) FROM calls"
    ).fetchone()[0]

    if existing == 0:
        seed(conn)
    else:
        print("Database already seeded")


if __name__ == "__main__":
    conn = get_connection()
    create_tables(conn)   # safe to call twice — uses IF NOT EXISTS
    seed(conn)
