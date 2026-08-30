"""
Vibhu-Oska AI-OS — SpecialistRouter
Routes tasks to appropriate specialists with load balancing.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

log = logging.getLogger("SpecialistRouter")


class SpecialistRouter:
    """
    Routes tasks to available specialists based on intent classification.

    Features:
    - Load balancing across available specialists
    - Health monitoring (remove unresponsive specialists)
    - Fallback to BackupCore if no specialist available
    """

    def __init__(self, backup_core: Any = None) -> None:
        self._specialists: dict[str, Any] = {}
        self._health: dict[str, bool] = {}
        self._load_counts: dict[str, int] = {}
        self._backup_core = backup_core
        self._route_count: int = 0

    def register(self, name: str, specialist: Any) -> None:
        """Register a specialist."""
        self._specialists[name] = specialist
        self._health[name] = True
        self._load_counts[name] = 0
        log.info(f"Registered specialist: {name}")

    def unregister(self, name: str) -> None:
        """Unregister a specialist."""
        self._specialists.pop(name, None)
        self._health.pop(name, None)
        self._load_counts.pop(name, None)

    def get_specialist(self, domain: str, subdomain: str = "") -> Optional[Any]:
        """
        Get the best available specialist for a domain.

        Returns specialist or None if unavailable.
        """
        candidates = []
        for name, specialist in self._specialists.items():
            if not self._health.get(name, False):
                continue

            if hasattr(specialist, "can_handle") and specialist.can_handle(domain, subdomain):
                load = self._load_counts.get(name, 0)
                candidates.append((name, specialist, load))

        if not candidates:
            return None

        # Pick least loaded
        candidates.sort(key=lambda x: x[2])
        name, specialist, _ = candidates[0]
        self._load_counts[name] = self._load_counts.get(name, 0) + 1
        return specialist

    async def route(
        self,
        domain: str,
        subdomain: str,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Route a task to the appropriate specialist.

        Falls back to BackupCore if no specialist available.
        """
        self._route_count += 1

        specialist = self.get_specialist(domain, subdomain)
        if specialist is not None:
            try:
                if hasattr(specialist, "process_with_tracking"):
                    result = await specialist.process_with_tracking(input_data)
                elif hasattr(specialist, "process"):
                    result = await specialist.process(input_data)
                else:
                    result = {"success": False, "error": "specialist_no_process"}

                return {
                    "success": True,
                    "result": result,
                    "specialist": getattr(specialist, "name", "unknown"),
                    "method": "specialist",
                }
            except Exception as e:
                log.warning(f"Specialist failed: {e}")
                return await self._fallback(input_data, str(e))

        return await self._fallback(input_data, "no_specialist_available")

    async def _fallback(
        self,
        input_data: dict[str, Any],
        reason: str,
    ) -> dict[str, Any]:
        """Fallback to BackupCore."""
        if self._backup_core is not None:
            try:
                if hasattr(self._backup_core, "process"):
                    result = await self._backup_core.process(input_data)
                else:
                    result = {"success": False, "error": "backup_no_process"}

                return {
                    "success": True,
                    "result": result,
                    "specialist": "BackupCore",
                    "method": "fallback",
                    "fallback_reason": reason,
                }
            except Exception as e:
                log.error(f"Backup fallback also failed: {e}")

        return {
            "success": False,
            "error": reason,
            "method": "failed",
        }

    def mark_unhealthy(self, name: str) -> None:
        """Mark a specialist as unhealthy."""
        self._health[name] = False
        log.warning(f"Specialist marked unhealthy: {name}")

    def mark_healthy(self, name: str) -> None:
        """Mark a specialist as healthy."""
        self._health[name] = True

    def get_metrics(self) -> dict[str, Any]:
        return {
            "route_count": self._route_count,
            "registered_specialists": len(self._specialists),
            "healthy_specialists": sum(1 for v in self._health.values() if v),
            "load_counts": self._load_counts.copy(),
        }
