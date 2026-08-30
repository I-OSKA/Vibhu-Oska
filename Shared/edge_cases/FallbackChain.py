"""
Vibhu-Oska AI-OS — Fallback Chain
Standard fallback logic when primary components fail.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional, Callable, Awaitable

log = logging.getLogger("FallbackChain")


@dataclass
class FallbackLevel:
    """A single level in the fallback chain."""
    name: str
    priority: int
    handler: Optional[Callable[..., Awaitable[Any]]] = None
    is_available: bool = True
    max_retries: int = 1


class FallbackChain:
    """
    Manages ordered fallback when primary components fail.

    Usage:
        chain = FallbackChain("inference")
        chain.add_level("paracore", priority=0)
        chain.add_level("specialist", priority=1)
        chain.add_level("backup", priority=2)
        chain.add_level("template", priority=3)
        result = await chain.execute(input_data)
    """

    def __init__(self, chain_name: str) -> None:
        self._chain_name = chain_name
        self._levels: list[FallbackLevel] = []
        self._execution_log: list[dict[str, Any]] = []

    def add_level(
        self,
        name: str,
        priority: int,
        handler: Optional[Callable[..., Awaitable[Any]]] = None,
        max_retries: int = 1,
    ) -> None:
        """Add a fallback level."""
        level = FallbackLevel(
            name=name,
            priority=priority,
            handler=handler,
            max_retries=max_retries,
        )
        self._levels.append(level)
        self._levels.sort(key=lambda x: x.priority)

    def mark_unavailable(self, name: str) -> None:
        """Mark a level as unavailable (e.g., after failure)."""
        for level in self._levels:
            if level.name == name:
                level.is_available = False
                log.warning(f"Fallback level '{name}' marked as unavailable")

    def mark_available(self, name: str) -> None:
        """Mark a level as available again."""
        for level in self._levels:
            if level.name == name:
                level.is_available = True
                log.info(f"Fallback level '{name}' marked as available")

    async def execute(
        self,
        input_data: dict[str, Any],
        exclude: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Execute through the fallback chain until one succeeds.

        Returns:
            {
                "success": bool,
                "result": Any,
                "level_used": str,
                "attempts": int,
                "log": list[dict],
            }
        """
        exclude = exclude or []
        attempts = 0
        execution_log = []

        for level in self._levels:
            if not level.is_available or level.name in exclude:
                continue

            if level.handler is None:
                log.debug(f"Skipping level '{level.name}' — no handler registered")
                continue

            for retry in range(level.max_retries):
                attempts += 1
                try:
                    log.info(
                        f"Fallback chain '{self._chain_name}': "
                        f"Trying level '{level.name}' (attempt {retry + 1}/{level.max_retries})"
                    )

                    result = await level.handler(input_data)

                    execution_log.append({
                        "level": level.name,
                        "attempt": retry + 1,
                        "success": True,
                    })

                    log.info(f"Fallback chain '{self._chain_name}': Level '{level.name}' succeeded")
                    return {
                        "success": True,
                        "result": result,
                        "level_used": level.name,
                        "attempts": attempts,
                        "log": execution_log,
                    }

                except Exception as e:
                    log.warning(
                        f"Fallback chain '{self._chain_name}': "
                        f"Level '{level.name}' failed (attempt {retry + 1}): {e}"
                    )
                    execution_log.append({
                        "level": level.name,
                        "attempt": retry + 1,
                        "success": False,
                        "error": str(e),
                    })

        # All levels exhausted
        log.error(f"Fallback chain '{self._chain_name}': All levels exhausted")
        return {
            "success": False,
            "result": None,
            "level_used": None,
            "attempts": attempts,
            "log": execution_log,
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "chain_name": self._chain_name,
            "levels": [
                {
                    "name": l.name,
                    "priority": l.priority,
                    "is_available": l.is_available,
                    "has_handler": l.handler is not None,
                }
                for l in self._levels
            ],
        }
