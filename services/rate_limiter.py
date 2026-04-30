import time


class InMemoryRateLimiter:
    def __init__(self, seconds=3):
        self._seconds = seconds
        self._last_request_at = {}

    def allow(self, key, now=None):
        current = now if now is not None else time.time()
        last = self._last_request_at.get(key, 0)
        if current - last < self._seconds:
            return False
        self._last_request_at[key] = current
        return True
