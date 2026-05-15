# File: constants.py
# Purpose: Central config — all hardcoded values live here, nowhere else
# Step: Step-1


# --- Database ---
DB_PATH = "db/calls.db"


# --- Per-token pricing in USD (input / output per 1000 tokens) ---
# Source: approximate public pricing at time of writing — update as needed
MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "llama-3.3-70b": {"input": 0.0009, "output": 0.0009},
}


# --- Seed config ---
SEED_ROW_COUNT = 75  # how many mock rows to generate
URGENCY_LEVELS = [1, 2, 3, 4, 5]
CALL_STATUSES = ["success", "success", "success", "error", "rate_limited"]
# success appears 3x so random.choice naturally weights it ~60%


# --- Tiktoken encoding map ---
# WHY: Different model families use different tokenizers.
# We map model name → tiktoken encoding so estimate_tokens() picks the right one.
# TODO: understand this — tiktoken encodings differ by model; cl100k_base is used
# by GPT-4 and GPT-3.5; llama models don't have official tiktoken support so we
# approximate with cl100k_base
MODEL_ENCODING = {
    "gpt-4o":          "cl100k_base",
    "gpt-3.5-turbo":   "cl100k_base",
    "llama-3.3-70b":   "cl100k_base",  # approximation — no official llama tiktoken
}


# --- OpenRouter / AI Analysis ---
OPENROUTER_API_URL  = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL    = "meta-llama/llama-3.3-70b-instruct"
ANALYSIS_LOG_LIMIT  = 100   # how many recent rows to send to the AI
MAX_AI_TOKENS       = 1000  # cap response length to control OpenRouter cost
