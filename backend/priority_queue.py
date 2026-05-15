# File: priority_queue.py
# Purpose: Orders pending LLM calls by urgency/cost ratio — highest value first
# Step: Step-3

import heapq
import threading
from typing import Any
from dataclasses import dataclass, field
from constants import URGENCY_LEVELS


# --- Constants ---
MIN_COST_FLOOR = 0.000001  # WHY: prevents division-by-zero if estimated_cost rounds to 0


@dataclass
class CallRequest:
    urgency:        int        # 1 (low) to 5 (critical)
    estimated_cost: float      # in USD, from estimate_tokens()
    model:          str
    prompt:         str
    metadata:       dict = field(default_factory=dict)  # any extra caller data


def _priority_score(request: CallRequest) -> float:
    # WHY: Higher urgency = more important. Higher cost = less desirable.
    # Dividing urgency by cost naturally ranks urgent cheap calls first.
    # Negated because heapq is a min-heap — we want highest score first.
    cost = max(request.estimated_cost, MIN_COST_FLOOR)
    return -(request.urgency / cost)


def _validate_request(request: CallRequest) -> None:
    # WHY: Catch bad data at push time, not silently during execution
    if request.urgency not in URGENCY_LEVELS:
        raise ValueError(f"urgency must be one of {URGENCY_LEVELS}, got {request.urgency}")
    if request.estimated_cost < 0:
        raise ValueError("estimated_cost cannot be negative")
    if not request.model:
        raise ValueError("model cannot be empty")


class CostAwarePriorityQueue:
    # WHY: Wraps heapq in a class so the lock, heap, and operations
    # stay together — callers never touch the raw heap

    def __init__(self) -> None:
        self._heap: list = []
        self._lock = threading.Lock()  # WHY: APScheduler runs background threads;
                                       # lock prevents race conditions on push/pop


    def push(self, request: CallRequest) -> None:
        # WHY: validate before acquiring lock — keeps locked section minimal
        _validate_request(request)
        score = _priority_score(request)
        with self._lock:
            heapq.heappush(self._heap, (score, request))


    def pop(self) -> CallRequest:
        # WHY: Raises clearly if empty — callers should check size() first
        with self._lock:
            if not self._heap:
                raise IndexError("Queue is empty")
            _, request = heapq.heappop(self._heap)
        return request


    def size(self) -> int:
        with self._lock:
            return len(self._heap)


    def peek(self) -> CallRequest:
        # WHY: Lets callers inspect next item without removing it
        with self._lock:
            if not self._heap:
                raise IndexError("Queue is empty")
            _, request = self._heap[0]
        return request
