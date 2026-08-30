"""
Vibhu-Oska AI-OS — OOM Handler
Monitors VRAM usage, performs emergency eviction, and CPU offload.
"""

from __future__ import annotations

import logging
from typing import Optional, Callable, Any

log = logging.getLogger("OOMHandler")


class OOMHandler:
    """
    Monitors VRAM usage and handles out-of-memory situations.

    Usage:
        handler = OOMHandler(vram_limit_gb=8.0)
        if handler.check_vram_available(required_gb=2.0):
            # safe to allocate
        else:
            handler.handleOOM()
    """

    def __init__(
        self,
        vram_limit_gb: float = 8.0,
        warning_threshold: float = 0.75,      # 75% = 6GB
        critical_threshold: float = 0.875,    # 87.5% = 7GB
        on_oom: Optional[Callable[[float, float], None]] = None,
    ) -> None:
        self._vram_limit_gb = vram_limit_gb
        self._warning_threshold = warning_threshold
        self._critical_threshold = critical_threshold
        self._on_oom = on_oom
        self._allocations: dict[str, float] = {}
        self._eviction_count: int = 0

    @property
    def warning_limit_gb(self) -> float:
        return self._vram_limit_gb * self._warning_threshold

    @property
    def critical_limit_gb(self) -> float:
        return self._vram_limit_gb * self._critical_threshold

    @property
    def total_allocated_gb(self) -> float:
        return sum(self._allocations.values())

    @property
    def available_gb(self) -> float:
        return max(0.0, self._vram_limit_gb - self.total_allocated_gb)

    def get_vram_usage(self) -> dict[str, float]:
        """Get current VRAM usage (requires torch)."""
        try:
            import torch
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / (1024**3)
                reserved = torch.cuda.memory_reserved() / (1024**3)
                return {
                    "allocated_gb": allocated,
                    "reserved_gb": reserved,
                    "limit_gb": self._vram_limit_gb,
                    "available_gb": self._vram_limit_gb - allocated,
                }
        except ImportError:
            pass
        return {
            "allocated_gb": self.total_allocated_gb,
            "reserved_gb": 0.0,
            "limit_gb": self._vram_limit_gb,
            "available_gb": self.available_gb,
        }

    def check_vram_available(self, required_gb: float) -> bool:
        """Check if enough VRAM is available for allocation."""
        usage = self.get_vram_usage()
        available = usage["available_gb"]
        return available >= required_gb

    def register_allocation(self, name: str, size_gb: float) -> None:
        """Register a VRAM allocation for tracking."""
        self._allocations[name] = size_gb
        log.info(f"Registered VRAM allocation: {name} = {size_gb:.2f}GB")

    def unregister_allocation(self, name: str) -> None:
        """Unregister a VRAM allocation."""
        if name in self._allocations:
            del self._allocations[name]
            log.info(f"Unregistered VRAM allocation: {name}")

    def handle_oom(
        self,
        required_gb: float,
        evictable_components: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Handle OOM situation.
        Returns action recommendations.
        """
        usage = self.get_vram_usage()
        available = usage["available_gb"]
        self._eviction_count += 1

        log.error(
            f"OOM Risk: Need {required_gb:.2f}GB, only {available:.2f}GB available. "
            f"Eviction #{self._eviction_count}"
        )

        if self._on_oom:
            self._on_oom(required_gb, available)

        # Determine what to evict
        evict_targets = []
        freed_gb = 0.0

        if evictable_components:
            for comp in evictable_components:
                if comp in self._allocations:
                    evict_targets.append(comp)
                    freed_gb += self._allocations[comp]
                    if freed_gb >= required_gb:
                        break

        action = "evict" if evict_targets else "reject"
        if freed_gb < required_gb and not evict_targets:
            action = "offload_to_cpu"
            log.warning("Insufficient evictable VRAM. Recommend CPU offload.")

        return {
            "action": action,
            "evict_targets": evict_targets,
            "freed_gb": freed_gb,
            "required_gb": required_gb,
            "available_gb": available,
            "eviction_count": self._eviction_count,
        }

    def get_metrics(self) -> dict[str, Any]:
        usage = self.get_vram_usage()
        return {
            "vram_limit_gb": self._vram_limit_gb,
            "vram_used_gb": usage["allocated_gb"],
            "vram_available_gb": usage["available_gb"],
            "utilization_pct": (usage["allocated_gb"] / self._vram_limit_gb) * 100,
            "eviction_count": self._eviction_count,
            "tracked_allocations": len(self._allocations),
        }
