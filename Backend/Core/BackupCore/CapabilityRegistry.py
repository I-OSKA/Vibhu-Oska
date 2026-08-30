"""
Vibhu-Oska AI-OS — CapabilityRegistry
Tracks what each backup model can do.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("CapabilityRegistry")


class CapabilityRegistry:
    """Registry of backup model capabilities."""

    def __init__(self) -> None:
        self._capabilities: dict[str, list[str]] = {}

    def register(self, model_name: str, capabilities: list[str]) -> None:
        """Register capabilities for a model."""
        self._capabilities[model_name] = capabilities
        log.info(f"Registered capabilities for {model_name}: {capabilities}")

    def unregister(self, model_name: str) -> None:
        self._capabilities.pop(model_name, None)

    def can_handle(self, model_name: str, capability: str) -> bool:
        """Check if a model has a specific capability."""
        return capability in self._capabilities.get(model_name, [])

    def find_models(self, capability: str) -> list[str]:
        """Find all models with a specific capability."""
        return [
            name for name, caps in self._capabilities.items()
            if capability in caps
        ]

    def get_metrics(self) -> dict[str, Any]:
        return {"registered_models": len(self._capabilities)}
