from __future__ import annotations

import time
from dataclasses import dataclass

from skyagentos.models.schemas import ErrorType


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay_s: float = 1.0
    max_delay_s: float = 8.0

    def delay_for(self, attempt: int) -> float:
        return min(self.base_delay_s * (2 ** max(0, attempt - 1)), self.max_delay_s)


def classify_error(exc: Exception) -> ErrorType:
    text = str(exc).lower()
    if "429" in text or "rate" in text:
        return ErrorType.RATE_LIMITED
    if "timeout" in text or "connection" in text:
        return ErrorType.NETWORK_ERROR
    if "policy" in text or "permission" in text:
        return ErrorType.POLICY_BLOCKED
    if "budget" in text:
        return ErrorType.BUDGET_EXCEEDED
    if "validation" in text:
        return ErrorType.VALIDATION_ERROR
    return ErrorType.TOOL_ERROR


def retry_sleep(policy: RetryPolicy, attempt: int) -> None:
    time.sleep(policy.delay_for(attempt))
