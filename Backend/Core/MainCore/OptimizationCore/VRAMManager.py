"""
Vibhu-Oska AI-OS — VRAMManager
Tracks and manages VRAM allocations.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("VRAMManager")


class VRAMManager:
    """Tracks all VRAM allocations and manages memory."""

    def __init__(self, total_vram_gb: float = 8.0) -> None:
        self._total_gb = total_vram_gb
        self._allocations: dict[str, float] = {}
        self._eviction_count: int = 0

    @property
    def total_gb(self) -> float:
        return self._total_gb

    @property
    def used_gb(self) -> float:
        return sum(self._allocations.values())

    @property
    def available_gb(self) -> float:
        return max(0, self._total_gb - self.used_gb)

    def allocate(self, name: str, size_gb: float) -> bool:
        """Allocate VRAM. Returns True if successful."""
        if size_gb > self.available_gb:
            log.warning(f"Cannot allocate {size_gb}GB for {name} — only {self.available_gb:.2f}GB available")
            return False
        self._allocations[name] = size_gb
        log.info(f"Allocated {size_gb:.2f}GB for {name}")
        return True

    def deallocate(self, name: str) -> None:
        """Deallocate VRAM."""
        self._allocations.pop(name, None)

    def get_lru_allocation(self) -> str | None:
        """Get the least recently used allocation."""
        if not self._allocations:
            return None
        return next(iter(self._allocations))

    def emergency_evict(self, required_gb: float) -> float:
        """Evict allocations until enough VRAM is available."""
        freed = 0.0
        while self.available_gb < required_gb and self._allocations:
            lru = self.get_lru_allocation()
            if lru:
                freed += self._allocations.pop(lru)
                self._eviction_count += 1
                log.warning(f"Emergency evicted: {lru}")
        return freed

    def get_metrics(self) -> dict[str, Any]:
        return {
            "total_gb": self._total_gb,
            "used_gb": self.used_gb,
            "available_gb": self.available_gb,
            "allocation_count": len(self._allocations),
            "eviction_count": self._eviction_count,
        }
