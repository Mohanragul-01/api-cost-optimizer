# test_cb.py
# Purpose: Simple test to verify CircuitBreaker logic works as expected
from circuit_breaker import CircuitBreaker


# WHY: This is a very basic test to ensure the CircuitBreaker class behaves as expected.
cb = CircuitBreaker('openai')


# WHY: We record 8 consecutive failures to trigger the circuit breaker into OPEN state.
for _ in range(8):
    cb.record_call(success=False)
# WHY: After 8 failures, the state should be OPEN, preventing further calls.
for _ in range(2):
    cb.record_call(success=True)


# WHY: Print the current state to verify it's OPEN and calls are being blocked.
print('openai state:', cb.get_state())
