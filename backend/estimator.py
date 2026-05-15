# File: estimator.py
# Purpose: Estimates token count + cost for a prompt before any API call is made
# Step: Step-2


import tiktoken
from constants import MODEL_PRICING, MODEL_ENCODING


# --- Constants ---
FALLBACK_ENCODING = "cl100k_base"  # used if model isn't in MODEL_ENCODING


def _get_encoder(model: str) -> tiktoken.Encoding:
    # WHY: Isolating encoder lookup means estimate_tokens() stays under 20 lines
    # and encoding errors are caught in one place
    encoding_name = MODEL_ENCODING.get(model, FALLBACK_ENCODING)
    return tiktoken.get_encoding(encoding_name)


def _count_tokens(text: str, encoder: tiktoken.Encoding) -> int:
    # WHY: Separated so we can unit-test token counting independently
    # from cost math
    return len(encoder.encode(text))


def estimate_tokens(prompt: str, model: str) -> dict:
    # WHY: Returns a dict (not just a number) so callers get everything
    # needed to make a queue/routing decision in one call
    if model not in MODEL_PRICING:
        raise ValueError(f"Unknown model '{model}'. Add it to MODEL_PRICING in constants.py")

    encoder = _get_encoder(model)
    prompt_tokens = _count_tokens(prompt, encoder)

    pricing = MODEL_PRICING[model]

    # WHY: We only know prompt tokens before the call — completion is unknown.
    # We estimate completion as 25% of prompt tokens as a conservative default.
    estimated_completion_tokens = max(1, prompt_tokens // 4)

    estimated_cost = round(
        (prompt_tokens / 1000) * pricing["input"] +
        (estimated_completion_tokens / 1000) * pricing["output"],
        6
    )

    return {
        "model":                      model,
        "prompt_tokens":              prompt_tokens,
        "estimated_completion_tokens": estimated_completion_tokens,
        "estimated_cost_usd":         estimated_cost,
        "pricing_used":               pricing,
    }
