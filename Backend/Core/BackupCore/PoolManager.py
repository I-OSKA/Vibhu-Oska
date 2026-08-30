"""
Vibhu-Oska AI-OS — PoolManager
Manages the BackupCore pool of generalist models.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("PoolManager")


class PoolManager:
    """Manages a pool of generalist backup models."""

    def __init__(self, max_pool_size: int = 4) -> None:
        self._max_size = max_pool_size
        self._pool: dict[str, Any] = {}
        self._load_order: list[str] = []

    def add(self, name: str, model: Any) -> bool:
        """Add a model to the pool."""
        if len(self._pool) >= self._max_size:
            # Evict LRU
            lru = self._load_order.pop(0)
            self._pool.pop(lru, None)
            log.info(f"Evicted LRU backup: {lru}")
        self._pool[name] = model
        self._load_order.append(name)
        return True

    def remove(self, name: str) -> None:
        """Remove a model from the pool."""
        self._pool.pop(name, None)
        if name in self._load_order:
            self._load_order.remove(name)

    def get(self, name: str) -> Any | None:
        """Get a model from the pool."""
        return self._pool.get(name)

    def get_available(self) -> list[str]:
        """Get names of available models."""
        return list(self._pool.keys())

    def get_metrics(self) -> dict[str, Any]:
        return {
            "pool_size": len(self._pool),
            "max_size": self._max_size,
            "models": list(self._pool.keys()),
        }
