import time
from typing import Any


class TTLCache:
    """Tiny in-memory TTL cache. Swap for Redis later without touching callers."""

    def __init__(self, ttl_seconds: int, max_items: int = 512):
        self.ttl = ttl_seconds
        self.max_items = max_items
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < time.monotonic():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        if len(self._store) >= self.max_items:
            self._store.pop(next(iter(self._store)))
        self._store[key] = (time.monotonic() + self.ttl, value)
