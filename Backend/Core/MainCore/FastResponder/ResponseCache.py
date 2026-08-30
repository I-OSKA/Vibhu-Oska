"""
Vibhu-Oska AI-OS — ResponseCache
LRU cache with TTL for FastResponder.
"""

from __future__ import annotations

import time
import logging
from collections import OrderedDict
from typing import Any, Optional

log = logging.getLogger("ResponseCache")


class ResponseCache:
    """LRU cache with TTL for fast response caching."""

    def __init__(self, max_size: int = 1000, ttl_s: float = 300.0) -> None:
        self._max_size = max_size
        self._ttl_s = ttl_s
        self._cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self._hits: int = 0
        self._misses: int = 0

    def get(self, key: str) -> Optional[str]:
        """Get a cached response."""
        if key in self._cache:
            value, ts = self._cache[key]
            if time.time() - ts < self._ttl_s:
                self._cache.move_to_end(key)
                self._hits += 1
                return value
            else:
                del self._cache[key]
        self._misses += 1
        return None

    def set(self, key: str, value: str) -> None:
        """Cache a response."""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (value, time.time())
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    def get_metrics(self) -> dict[str, Any]:
        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.hit_rate,
        }
