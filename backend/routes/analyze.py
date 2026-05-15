# File: routes/analyze.py
# Purpose: POST /api/analyze — pulls recent logs, asks Llama 3.3 for routing
#          recommendations, validates and returns structured JSON
# Step: Step-6

import os
import json
import requests
from flask        import Blueprint, jsonify
from dotenv       import load_dotenv
from db.schema    import get_connection
from constants    import (OPENROUTER_API_URL, OPENROUTER_MODEL,
                          ANALYSIS_LOG_LIMIT, MAX_AI_TOKENS)


load_dotenv()  # WHY: loads .env into os.environ before we read the key


# --- Constants ---
REQUIRED_KEYS = {"recommendations", "projected_savings_usd", "summary"}

analyze_bp = Blueprint("analyze", __name__)


# ── DB helpers ────────────────────────────────────────────────────────────────

def _fetch_log_summary(conn) -> list[dict]:
    # WHY: We send a summary, not raw rows — keeps the prompt short and focused
    rows = conn.execute(f"""
        SELECT model, status, actual_cost, prompt_tokens,
               completion_tokens, urgency, timestamp
        FROM   calls
        ORDER  BY timestamp DESC
        LIMIT  {ANALYSIS_LOG_LIMIT}
    """).fetchall()
    return [dict(r) for r in rows]


def _build_stats(rows: list[dict]) -> dict:
    # WHY: Aggregate numbers give the AI context without sending 100 raw rows
    total_cost   = sum(r["actual_cost"] for r in rows)
    error_count  = sum(1 for r in rows if r["status"] == "error")
    model_counts: dict = {}
    for r in rows:
        model_counts[r["model"]] = model_counts.get(r["model"], 0) + 1
    return {
        "total_cost_usd": round(total_cost, 6),
        "error_count":    error_count,
        "call_count":     len(rows),
        "model_breakdown": model_counts,
    }


# ── Prompt builder ────────────────────────────────────────────────────────────

def _build_prompt(rows: list[dict]) -> str:
    # WHY: Structured prompt with explicit JSON schema forces the model to
    # return parseable output — reduces hallucinated formats
    stats = _build_stats(rows)
    return f"""
You are an LLM API cost optimization expert.
Analyze the following API usage summary and return ONLY a JSON object.

Usage summary:
{json.dumps(stats, indent=2)}

Recent calls sample (last 10):
{json.dumps(rows[:10], indent=2)}

Return ONLY this JSON structure — no extra text, no markdown fences:
{{
  "summary": "one sentence overview of cost health",
  "recommendations": [
    {{
      "title": "short action title",
      "detail": "one sentence explanation",
      "estimated_saving_usd": 0.00
    }}
  ],
  "projected_savings_usd": 0.00
}}
""".strip()


# ── OpenRouter call ───────────────────────────────────────────────────────────

def _call_openrouter(prompt: str) -> str:
    # WHY: Isolated so we can mock this in tests without hitting the real API
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENROUTER_API_KEY not set in .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
    }
    body = {
        "model":      OPENROUTER_MODEL,
        "max_tokens": MAX_AI_TOKENS,
        "messages":   [{"role": "user", "content": prompt}],
    }
    resp = requests.post(OPENROUTER_API_URL, headers=headers,
                         json=body, timeout=30)
    resp.raise_for_status()  # WHY: surfaces HTTP errors immediately as exceptions
    return resp.json()["choices"][0]["message"]["content"]


# ── JSON validator ────────────────────────────────────────────────────────────

def _parse_and_validate(raw: str) -> dict:
    # WHY: LLMs sometimes wrap JSON in ```json fences — strip before parsing
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = json.loads(clean)  # raises json.JSONDecodeError if malformed

    missing = REQUIRED_KEYS - parsed.keys()
    if missing:
        raise ValueError(f"AI response missing required keys: {missing}")

    return parsed


# ── Route ─────────────────────────────────────────────────────────────────────

@analyze_bp.route("/api/analyze", methods=["POST"])
def post_analyze():
    try:
        conn   = get_connection()
        rows   = _fetch_log_summary(conn)
        conn.close()

        if not rows:
            return jsonify({"error": "No call logs found — run seed.py first"}), 400

        prompt  = _build_prompt(rows)
        raw     = _call_openrouter(prompt)
        result  = _parse_and_validate(raw)
        return jsonify(result), 200

    except EnvironmentError as e:
        return jsonify({"error": str(e)}), 500
    except requests.HTTPError as e:
        return jsonify({"error": f"OpenRouter HTTP error: {e}"}), 502
    except (json.JSONDecodeError, ValueError) as e:
        # WHY: Never forward raw LLM output on parse failure — return a safe error
        return jsonify({"error": f"AI response unparseable: {e}"}), 502

