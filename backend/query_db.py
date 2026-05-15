import sqlite3
import sys, os

# Add parent directory to path for importing constants
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from constants import DB_PATH


def count():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM calls;")
    result = cursor.fetchone()
    conn.close()
    return result[0]


def sample():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT model, status, actual_cost FROM calls LIMIT 5;")
    result = cursor.fetchall()
    conn.close()
    return result


if __name__ == "__main__":
    # count = count()
    # print(f"Total rows in calls table: {count}")
    sample = sample()
    print(f"Sample rows: {sample}")
