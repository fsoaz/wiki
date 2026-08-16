from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException


class FixedWindowRateLimiter:
    """Small single-process limiter for the one-instance MVP runtime."""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = monotonic()
        cutoff = now - window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                retry_after = max(1, int(events[0] + window_seconds - now) + 1)
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(retry_after)},
                )
            events.append(now)
            while len(self._events) > 10_000:
                oldest_key = next(iter(self._events))
                if oldest_key == key and len(self._events) > 1:
                    oldest_key = next(iter(list(self._events)[1:]))
                self._events.pop(oldest_key, None)

    def reset(self) -> None:
        with self._lock:
            self._events.clear()


rate_limiter = FixedWindowRateLimiter()
